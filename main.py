import os
from typing import Union, Literal, List
import logging
from urllib.parse import unquote
import json

from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from mangum import Mangum
import uvicorn
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

RUNNING_IN_LAMBDA = os.environ.get("LAMBDA_TASK_ROOT")

S3_BUCKET_NAME: str = "videocloud-s3"
S3_UPLOAD_FOLDER: str = "uploads/"
S3_DOWNLOAD_FOLDER: str = "rendered/"

tasks_types = ["render", "segment", "obj_detect"]

aws_config = Config(
    region_name="us-east-1",
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"},
)

if RUNNING_IN_LAMBDA:
    AWS_ACCESS_KEY = None
    AWS_SECRET_ACCESS_KEY = None

    s3_client = boto3.client("s3", config=aws_config)
    lambda_client = boto3.client("lambda", config=aws_config)
else:
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not AWS_ACCESS_KEY or not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY must be set")

    s3_client = boto3.client(
        "s3_client",
        config=aws_config,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    lambda_client = boto3.client(
        "lambda",
        config=aws_config,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


app = FastAPI()
handler = Mangum(app)


class RenderVideo(BaseModel):
    tasks: List[str]


@app.get("/")
def read_root():
    return {"API": "Healthy"}


@app.get("/upload-url")
def get_upload_url(filename: str = None):
    if not filename:
        raise HTTPException(status_code=422, detail="Missing parameter: filename")

    bucket = S3_BUCKET_NAME
    key = S3_UPLOAD_FOLDER + unquote(filename)

    logging.info("generating presigned upload url for bucket: %s, key: %s", bucket, key)

    url = generate_presigned_url("put_object", bucket, key)
    return {"data": url}


@app.get("/download-url")
def get_download_url(filename: str = None):

    if not filename:
        raise HTTPException(status_code=422, detail="Missing parameter: filename")

    bucket = S3_BUCKET_NAME
    key = S3_DOWNLOAD_FOLDER + unquote(filename)

    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as err:
        logging.debug(err)
        raise HTTPException(status_code=404, detail="File not found")

    bucket = S3_BUCKET_NAME
    key = S3_DOWNLOAD_FOLDER

    logging.info(
        "generating presigned download url for bucket: %s, key: %s", bucket, key
    )

    url = generate_presigned_url("get_object", bucket, key)

    return {"data": url}


@app.post("/render")
def render_video(filename: str, body: RenderVideo):

    for task in body.tasks:
        if task not in tasks_types:
            raise HTTPException(status_code=422, detail="Invalid task type")

    payload = json.dumps({"filename": filename, "tasks": body.tasks})

    logging.info("Invoking lambda function with payload: %s", payload)

    # RequestResponse invokes the function synchronously.
    response = lambda_client.invoke(
        FunctionName="videocloud-ffmpeg",
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=payload,
    )

    return {"data": response}


def generate_presigned_url(
    client_method: Union[Literal["get_object"], Literal["put_object"]],
    bucket_name: str,
    object_name: str,
    expiration: int = 200,
):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param s3_client: A Boto3 Amazon S3 client.
    :param client_method: The name of the client method that the URL performs. put_object, get_object, etc.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method,
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        logging.info("Got presigned URL: %s", url)
    except ClientError:
        logging.exception(
            "Couldn't get a presigned URL for client method '%s'.", client_method
        )
        raise
    return url


if __name__ == "__main__":
    uvicorn.run(
        app="main:app", host="127.0.0.1", port=8000, log_level="info", reload=True
    )
    print("videocloud running")

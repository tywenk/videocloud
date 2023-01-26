from typing import Union, Literal
import logging
from urllib.parse import unquote

from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from mangum import Mangum
import uvicorn

from aws_client import AWSClient

aws_client = AWSClient()
s3 = aws_client.s3

app = FastAPI()
handler = Mangum(app)

origins = ["http://localhost:8000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"API": "Healthy"}


@app.get("/upload-url")
def get_upload_url(filename: str = None):
    if not filename:
        raise HTTPException(status_code=422, detail="Missing parameter: filename")

    bucket = aws_client.S3_BUCKET_NAME
    key = aws_client.S3_UPLOAD_FOLDER + unquote(filename)
    url = generate_presigned_url(s3, "put_object", bucket, key)
    return {"data": url}


@app.get("/download-url")
def get_download_url():
    bucket = aws_client.S3_BUCKET_NAME
    key = aws_client.S3_DOWNLOAD_FOLDER
    url = generate_presigned_url(s3, "get_object", bucket, key)
    return {"data": url}


def generate_presigned_url(
    s3_client,
    client_method: Union[Literal["get_object"], Literal["put_object"]],
    bucket_name: str,
    object_name: str,
    expiration: int = 100,
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

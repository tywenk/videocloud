import os
from dataclasses import dataclass
import boto3
from botocore.config import Config

@dataclass
class AWSClient():
    
    S3_BUCKET_NAME: str = "videocloud-s3"
    S3_UPLOAD_FOLDER: str = "uploads/"
    S3_DOWNLOAD_FOLDER: str = "rendered/"
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not AWS_ACCESS_KEY or not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY must be set")
    
    aws_config = Config(
        region_name="us-east-1",
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )
    
    s3 = boto3.client(
        "s3",
        config=aws_config,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    

        

        
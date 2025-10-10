import boto3
import os
import uuid

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
BUCKET_UP = os.getenv("S3_BUCKET_UPLOADS")
BUCKET_OUT = os.getenv("S3_BUCKET_OUTPUTS")


def presign_put_url(filename: str) -> dict:
    key = f"uploads/{uuid.uuid4()}-{filename}"
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": BUCKET_UP, "Key": key, "ContentType": "audio/mpeg"},
        ExpiresIn=3600,
    )
    return {"key": key, "url": url}


def presign_get_url(bucket: str, key: str, expires: int = 3600) -> str:
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires,
    )


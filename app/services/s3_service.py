import boto3
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET

s3_client = boto3.client('s3', 
                        region_name=AWS_REGION,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        config=boto3.session.Config(signature_version='s3v4'))

def upload_file(file_path, s3_path):
    s3_client.upload_file(file_path, S3_BUCKET, s3_path)
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_path}" 
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_pdf_to_s3(local_pdf_path: str, s3_bucket: str, s3_key: str) -> str:
    """
    Upload a PDF to S3 and return the public URL or presigned URL.
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            Filename=local_pdf_path,
            Bucket=s3_bucket,
            Key=s3_key,
            ExtraArgs={"ContentType": "application/pdf"}
        )
        return f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"
    except FileNotFoundError:
        raise Exception("The file to upload was not found.")
    except NoCredentialsError:
        raise Exception("AWS credentials were not found.")
    except ClientError as e:
        raise Exception(f"Failed to upload PDF to S3: {e}")

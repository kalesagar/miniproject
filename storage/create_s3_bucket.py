import boto3
import os
# Configure AWS credentials
session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-1'
)

# Create an S3 client
s3_client = session.client('s3')
bucket_name = 'ccgroup18-bucket'
# Create an S3 bucket
def create_bucket(bucket_name):
    try:
        response = s3_client.create_bucket(
            Bucket=bucket_name
        )
        print('Bucket created successfully')
    except s3_client.exceptions.ClientError as e:
        print('Error creating bucket:', e)

def upload_file(bucket_name, filename):
    try:
        create_bucket(bucket_name)
        s3_client.upload_file(
            Filename=filename,
            Bucket=bucket_name,
            Key=filename
        )
        print('File uploaded successfully')
    except s3_client.exceptions.ClientError as e:
        print('Error uploading file:', e)
        
def retrieve_files(bucket_name):
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name
        )
        return response
    except s3_client.exceptions.ClientError as e:
        print('Error retrieving files:', e)
        
def get_presigned_url(bucket_name, filename):
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename
            },
            ExpiresIn=3600
        )
        return presigned_url
    except s3_client.exceptions.ClientError as e:
        print('Error generating presigned URL:', e)
# Usage example


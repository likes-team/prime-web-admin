import os
import logging
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename


SESSION = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)


def upload_file(file, file_name, folder_name="cash_flow/"):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    # Upload the file
    s3_client = SESSION.resource("s3")
    bucket_name = "primeklcbucket"
    bucket = s3_client.Bucket(bucket_name)

    try:
        file_path = folder_name + "{}".format(file_name)
        bucket.Object(file_path).put(Body=file)
        object_url = "https://primeklcbucket.s3.ap-southeast-1.amazonaws.com/{}".format(
            file_path
        )
        return object_url
    except ClientError as e:
        logging.error(e)
        return None

def delete_file(file_name, folder_name="cash_flow/"):
    """Delete a file from an S3 bucket

    :param file_name: File name to delete
    :param folder_name: Folder where the file is located
    :return: True if the file was deleted, else False
    """
    s3_client = SESSION.resource("s3")
    bucket_name = "primeklcbucket"
    bucket = s3_client.Bucket(bucket_name)

    try:
        # Construct the file path
        file_path = folder_name + "{}".format(file_name)
        
        # Delete the file
        bucket.Object(file_path).delete()
        
        return True
    except ClientError as e:
        logging.error(e)
        return False

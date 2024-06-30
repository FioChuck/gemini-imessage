import json

from functions import *
from compute import *
import requests


def download_text_from_gcs(project_id, bucket_name, file_name):
    """Downloads text content from a file in GCS."""

    storage_client = storage.Client(project=project_id)  # Specify project ID
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    text_content = blob.download_as_text()

    print(
        f"File {file_name} downloaded from bucket {bucket_name} in project {project_id}")
    return text_content


def upload_text_to_gcs(project_id, bucket_name, file_name, text_content):
    """Uploads text content to a file in GCS."""

    storage_client = storage.Client(project=project_id)  # Specify project ID
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_string(text_content, content_type='text/plain')

    print(
        f"File {file_name} uploaded to bucket {bucket_name} in project {project_id}")


def run(**kwargs):

    try:

        url = os.getenv('URL')
        sender = os.getenv('SENDER')

        payload = json.dumps({
            "limit": 1,
            "offset": 0,
            "chatGuid": "SMS;-;" + sender,
            "with": [
                "chat",
                "chat.participants",
                "attachment",
                "handle",
                "sms"
            ],
            "sort": "DESC"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_dict = response.json()

        project_id = "fiorenza-house-hunt"
        bucket_name = "cf-imessage-status"
        file_name = "status.txt"

        text_content = download_text_from_gcs(
            project_id, bucket_name, file_name)

        if text_content != response_dict["data"][0]["text"] and response_dict["data"][0]["isFromMe"] is not True:
            print("-------------------------------")
            print("new message received!")
            print("message says: " + response_dict["data"][0]["text"])
            print("-------------------------------")

            text_content = str(response_dict["data"][0]["text"])

            upload_text_to_gcs(project_id, bucket_name,
                               file_name, text_content)
        else:
            print("invalid message")

    except Exception as e:
        print(e)

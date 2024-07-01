import json
from functions import *
from compute import *
from gemini import *
import requests


def download_text_from_gcs(project_id, bucket_name, file_name):

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    text_content = blob.download_as_text()

    return text_content


def upload_text_to_gcs(project_id, bucket_name, file_name, text_content):

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_string(text_content, content_type='text/plain')

    return "complete"


def run(**kwargs):

    try:

        bb_url = os.getenv('BB_URL')
        sender = os.getenv('SENDER')
        pw = os.getenv('PW')

        url = bb_url + "/api/v1/message/query?password=" + pw

        payload = json.dumps({
            "limit": 1,
            "offset": 0,
            "chatGuid": sender,
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

        print("Request from BlueBubbles: " + str(response.json()))

        response_dict = response.json()

        project_id = "fiorenza-house-hunt"
        bucket_name = "cf-imessage-status"
        file_name = "status.txt"

        text_content = download_text_from_gcs(
            project_id, bucket_name, file_name)

        print("Last message received: " + text_content)

        if text_content != response_dict["data"][0]["text"] and response_dict["data"][0]["isFromMe"] is not True:
            print("-------------------------------")
            print("New Message Received!")
            print("Message Says: " + response_dict["data"][0]["text"])
            print("-------------------------------")

            text_content = str(response_dict["data"][0]["text"])

            upload_text_to_gcs(project_id, bucket_name,
                               file_name, text_content)

            update_context(response_dict)

        else:
            print(
                "Invalid Message - Either wrong contact, duplicate message, or message is from sender")

    except Exception as e:
        print(e)

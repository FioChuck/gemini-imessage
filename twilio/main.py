import json
import threading
import functions_framework
from functions import *
from compute import *
import requests
from dotenv import load_dotenv


@functions_framework.http
def main(request):

    # data = request.form

    if request.method == "OPTIONS":

        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    url = os.getenv('URL')

    payload = json.dumps({
        "limit": 1,
        "offset": 0,
        "chatGuid": "SMS;-;+16504046137",
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

    print(response.text)

# print("starting threaded app")

# thread = threading.Thread(target=run, kwargs={
#     'dtype': dtype,
#     'body': body,
#     'num_media': data["NumMedia"],
#     'sms_sid': data["SmsSid"],
#     'sms_from': data["From"],
#     'media_url': url})
# thread.start()

    return ("done", 200, headers)

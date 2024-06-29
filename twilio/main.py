import threading
import functions_framework
from functions import *
from compute import *


@functions_framework.http
def main(request):

    data = request.form

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

    print("ulr?: " + str(("MediaUrl0" in data)))
    print("body?: " + str(("Body" in data)))

    body_flag = False

    print(type(data))
    print(data)

    # try:
    #     if data["Body"] != "":
    #         body_flag = True
    #     else:
    #         body_flag = False

    # except:
    #     print("no Body field")

    # print("body flag " + str(body_flag))

    # if ("MediaUrl0" in data) & ("Body" in data) & (body_flag):
    #     print("processing sms and mms")
    #     dtype = "both"
    #     url = data["MediaUrl0"]
    #     body = data["Body"]
    # elif ("MediaUrl0" in data) & (("Body" not in data) | (not body_flag)):
    #     print("processing mms")
    #     dtype = "mms"
    #     url = data["MediaUrl0"]
    #     body = ""
    # elif ("MediaUrl0" not in data) & ("Body" in data):
    #     print("processing sms")
    #     dtype = "sms"
    #     url = ""
    #     body = data["Body"]

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

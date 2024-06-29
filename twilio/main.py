import json
import threading
import functions_framework
from functions import *
from compute import *
from datetime import datetime


def print_message_received():
    """Prints a message with the current timestamp."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"Message received at: {timestamp}")


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

    # Call the function to print the message
    print_message_received()

    thread = threading.Thread(target=run, kwargs={})
    thread.start()

    return ("done", 200, headers)

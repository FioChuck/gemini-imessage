from google.cloud import storage
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel

from twilio.process import *


def prepend_to_gcs_file(bucket_name, file_name, text_to_prepend):
    """Prepends text to the top of a file in Google Cloud Storage."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download existing content
    existing_content = blob.download_as_text()

    # Combine new and existing content
    new_content = text_to_prepend + existing_content

    # Upload the new content
    blob.upload_from_string(new_content)


def generate_response():
    print("done")

    vertexai.init(project="fiorenza-house-hunt", location="us-central1")

    model = GenerativeModel("gemini-1.0-pro-002")

    context = download_text_from_gcs(
        "fiorenza-house-hunt", "cf-imessage-status", "context.txt")

    response = model.generate_content(
        "You are an intelligent text message responding agent named Chas Fiorenza. You are communicated with Jamie Wagner who goes by Wags. \
        Wags is roughly 50 years old and coaches highschool baseball. He loves playing video games (mainly Call of Duty) and the New York Yankees. \
        He sometimes goes by VognerPosiden. Please respond to this conversation in short casual form and never conceal your identity as a LLM. \
        The following text includes context from previous conversations. Text that starts with 'Sent' represents messages sent to Wags. \
        Text that starts with 'Received' represents messages sent by wags to you (Chas). Respond to the most recent received item." + context)

    print(response)

    print(type(response))

    return response


def update_context(message):
    # Example usage
    bucket_name = "cf-imessage-status"
    file_name = "context.txt"

    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    received = "Received at " + \
        str(event_time) + ". Content: " + message["data"][0]["text"] + "\n"
    sent = "Sent at " + \
        str(event_time) + ". Content: " + "This is a test response" + "\n"

    prepend_to_gcs_file(bucket_name, file_name, received)

    generate_response()

    prepend_to_gcs_file(bucket_name, file_name, sent)

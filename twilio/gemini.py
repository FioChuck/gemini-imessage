from google.cloud import storage
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel


def load_context(project_id, bucket_name, file_name):
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text_content = blob.download_as_text()
    return text_content


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

    vertexai.init(project="fiorenza-house-hunt", location="us-central1")

    model = GenerativeModel("gemini-1.0-pro-002")

    context = load_context(
        "fiorenza-house-hunt", "cf-imessage-status", "context.txt")

    responses = model.generate_content(
        "You are an intelligent text message responding agent named Chas Fiorenza. You are communicated with Jamie Wagner who goes by Wags. \
        Wags is roughly 50 years old and coaches highschool baseball. He loves playing video games (mainly Call of Duty) and the New York Yankees. \
        He sometimes goes by VognerPosiden. Please respond to this conversation in short casual form and never reveal your identity as a LLM. \
        The following text includes context from previous conversations. Text that starts with 'Sent' represents messages sent to Wags. \
        Text that starts with 'Received' represents messages sent by wags to you (Chas). Respond to the most recent received item. Please do not use emojis in your response." + context)

    output = ""

    for response in responses:
        output = output + str(response.text)

    print("Gemini response: " + output)

    return output


def update_context(message):

    bucket_name = "cf-imessage-status"
    file_name = "context.txt"

    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    received = "Received at " + \
        str(event_time) + ". Content: " + message["data"][0]["text"] + "\n"

    prepend_to_gcs_file(bucket_name, file_name, received)

    gemini_text = generate_response()

    sent = "Sent at " + \
        str(event_time) + ". Content: " + gemini_text + "\n"

    prepend_to_gcs_file(bucket_name, file_name, sent)

from google.cloud import storage
from datetime import datetime


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


def update_context(message):
    # Example usage
    bucket_name = "cf-imessage-status"
    file_name = "context.txt"

    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    received = "Received: " + ["data"][0]["text"] + "\n"
    sent = "Sent: " + "This is a test response" + "\n"

    prepend_to_gcs_file(bucket_name, file_name, str(event_time))
    prepend_to_gcs_file(bucket_name, file_name, received)
    prepend_to_gcs_file(bucket_name, file_name, sent)

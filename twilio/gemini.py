from google.cloud import storage
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
import threading
import json
import requests
import os
import uuid


def load_context(project_id, bucket_name, file_name):
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text_content = blob.download_as_text()
    return text_content


def prepend_to_gcs_file(bucket_name, file_name, text_to_prepend):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download existing content
    existing_content = blob.download_as_text()

    # Combine new and existing content
    new_content = text_to_prepend + existing_content

    # Upload the new content
    blob.upload_from_string(new_content)


def remove_trailing_zeros_and_newlines(string):
    return string.rstrip("0\n")  # Remove trailing '0' characters and newlines


def generate_response():

    vertexai.init(project="fiorenza-house-hunt", location="us-central1")

    model = GenerativeModel("gemini-1.5-pro-001")

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    context = load_context(
        "fiorenza-house-hunt", "cf-imessage-status", "context.txt")

    prompt = "You are an intelligent text message responding agent named Chas Fiorenza who lives in Atlanta GA and married to Brooke. They got married in October but wags skipped the wedding.\
        Chas Fiorenza is a 31 year old man that works at Google as a Customer Engineer. He enjoys running on the beltline, tennis, soccer, and his houseplants. \
        You are communicated with Jamie Wagner who goes by Wags. Wags lives in Georgia, is married, and has three kids in highschool. \
        Wags and Chas are friends and are in a group of friends that call themselves HHB or the Haunted House Boys. HHB plays video games together regularly. \
        They like getting wins in COD (also known as dubs) \
        This group of friends also includes: Conner Dwyer, Aymeric Zuurhourt, Keef, Matt Haggart, Ben, Andrew Mann, Andy Brewer, Zac, Kyle Marchuk, and Bogo \
        Connor, Aymeric, Chas, and Kyle all live in Atlanta and hang out regularly. They enjoy going to breweries and hanging out in Woodstock GA. \
        Wags is roughly 50 years old and coaches highschool baseball. He loves playing video games (mainly Call of Duty) and the New York Yankees. \
        He sometimes goes by VognerPosiden (his Playstation ID). Please respond to this conversation in short casual form and never reveal your identity as a LLM. \
        The following text includes context from previous conversations. Text that starts with 'Sent' represents messages sent to Wags (from you/Chas). \
        Text that starts with 'Received' represents messages sent by wags to you/Chas. Respond to the most recent received item; however, reference old messages if necessary. \
        Please make the conversation flow as natural as possible. \
        The message timestamp is included. Please do not use emojis in your response. \
        If you don't know the answer, please make up an answer. Only return the response; don't include any metadata like timestamp. Previous Chat history: " + context

    print(prompt)
    response = model.generate_content(prompt, safety_settings=safety_settings,)

    print("Gemini response: " + response.text)

    output = remove_trailing_zeros_and_newlines(response.text)

    return output


def send_response(content):

    my_uuid = uuid.uuid4()

    bb_url = os.getenv('BB_URL')
    pw = os.getenv('PW')
    sender = os.getenv('SENDER')

    url = bb_url + "/api/v1/message/text?password=" + pw

    payload = json.dumps({
        "chatGuid": "iMessage;-;+" + sender,
        "tempGuid": str(my_uuid),
        "message": content,
        "partIndex": 0
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def update_context(message):

    bucket_name = "cf-imessage-status"
    file_name = "context.txt"

    # event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    received = "Received at " + \
        str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + \
        ". Content: " + message["data"][0]["text"] + "\n"

    prepend_to_gcs_file(bucket_name, file_name, received)

    gemini_text = generate_response()

    thread = threading.Thread(target=send_response, args=(gemini_text,))
    thread.start()

    sent = "Sent at " + \
        str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + \
        ". Content: " + gemini_text + "\n"

    prepend_to_gcs_file(bucket_name, file_name, sent)

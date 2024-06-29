
from hashlib import sha256
from dotenv import load_dotenv
import requests
import os
from google.cloud import storage
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import datetime


def upload_blob(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0

    blob.upload_from_filename(
        source_file_name, if_generation_match=generation_match_precondition)


def number_mask(hash_str):

    # dotenv used to test salt secret locally
    load_dotenv()

    # load salt secret
    key = os.getenv('HMAC_VAL')

    # concatenate hash and salt
    val = hash_str + key

    # hash the concatenated string
    out = sha256(val.encode('utf-8')).hexdigest()

    return out


def mms_process(media_url, sms_id):

    # unique identifier used as file name
    filename = sms_id + ".png"

    with open(filename, 'wb') as f:
        image_url = media_url
        f.write(requests.get(image_url).content)


def save_results_collection1(id, user, file):

    # ct stores current time
    ct = datetime.datetime.now()

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()

    doc_ref = db.collection("gemini-demo-text").document(id)
    doc_ref.set({"user": user, "fileName": file,
                "fileLocation": "https://storage.cloud.google.com/twillio-images/" + file,
                 "timeStamp": ct})


def save_results_collection2(id, bucket, file):

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()

    doc_ref = db.collection("gemini-demo-text-result").document(id)
    doc_ref.set({"fileName": file,
                "fileLocation": "https://storage.googleapis.com/" + bucket + "/" + file,
                 "query": "",
                 "result": "",
                 "timeStamp": None})


def update_collection2(id, query, result):

    # ct stores current time
    ct = datetime.datetime.now()

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()

    doc = db.collection("gemini-demo-text-result").document(id)

    doc.update({"query": query, "result": result, "timeStamp": ct})


def return_image(user):

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()

    docs = (
        db.collection("gemini-demo-text")
        .where(filter=FieldFilter("user", "==", user))
        .order_by("timeStamp").limit_to_last(1)
        .get()
    )

    for doc in docs:
        output = doc.to_dict()

    return output


def generate_text(project_id: str, location: str, file: str, query: str) -> str:
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    # Load the model
    multimodal_model = GenerativeModel("gemini-pro-vision")
    # Query the model
    query = "You are a knowledgeable agent. You are brief in your answers and " + \
            "respond in only one or two sentences without extra verbiage. Please " + \
            "answer the following user question: \n\n" + query
    response = multimodal_model.generate_content(
        [
            Part.from_uri(
                file, mime_type="image/png"
            ),
            query
        ]
    )
    return response.text

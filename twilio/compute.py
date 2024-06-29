import time
from functions import *


def run(**kwargs):

    delay = 15

    try:
        sms_sid = kwargs.get('sms_sid', {})
        sms_from = kwargs.get('sms_from', {})
        body = kwargs.get('body', {})
        media_url = kwargs.get('media_url', {})
        dtype = kwargs.get('dtype', {})


        project = os.getenv('PROJECT')
        loc = os.getenv('LOCATION')
        bucket_name = os.getenv('GCS_BUCKET')

        # process multimedia messages (mms)
        if dtype == "mms":

            # download image twillio to vm
            mms_process(media_url, sms_sid)

            #  set filename of images sent to gcs. Use unique identifier sms_from twillio
            filename = sms_sid + ".png"

            # Upload image to gcs bucket
            upload_blob(bucket_name, filename, filename)

            # save metadata to firestore collection 1 (filename, masked identifier)
            save_results_collection1(
                sms_sid, number_mask(sms_from), filename)

            # create results doc (collection 2)
            save_results_collection2(sms_sid, bucket_name,filename)

        elif dtype == "both":

            # download image sms_from twillio
            mms_process(media_url, sms_sid)

            #  set filename of images sent to gcs. Use unique identifier sms_from twillio
            filename = sms_sid + ".png"

            # Upload image to gcs bucket
            upload_blob(bucket_name, filename, filename)

            # save metadata to firestore collection 1 (filename, masked identifier)
            save_results_collection1(
                sms_sid, number_mask(sms_from), filename)

            # create results doc
            save_results_collection2(sms_sid,bucket_name, filename)

            ################################## processes text #################################

            doc = return_image(number_mask(sms_from))

            filename = doc["fileName"]

            # construct gsl using filename
            path = "gs://" + bucket_name + "/" + filename  # uri

            # genrate response using gemini
            genai_ouput = generate_text(
                project, loc, path, body)

            update_collection2(doc["fileName"].split(
                ".")[0], body, genai_ouput)

        # process text messages
        elif dtype == "sms":

            for i in range(delay):
                time.sleep(1)
                # print(i)

            doc = return_image(number_mask(sms_from))

            filename = doc["fileName"]

            # construct gsl using filename
            path = "gs://" + bucket_name + "/" + filename  # uri

            # genrate response using gemini
            genai_ouput = generate_text(
                project, loc, path, body)

            # upload results to firestore
            update_collection2(doc["fileName"].split(
                ".")[0], body, genai_ouput)

    except Exception as e:
        print(e)
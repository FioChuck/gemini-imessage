# gcloud storage buckets create gs://gemini-cloud-function-source

gcloud storage buckets create gs://gemini-demo-images --location=us-central1; gcloud storage buckets add-iam-policy-binding gs://gemini-demo-images --member=allUsers --role=roles/storage.objectViewer


gcloud storage buckets create gs://cf-gemini-demo-app-host --location=us-central1
gcloud storage buckets add-iam-policy-binding gs://cf-gemini-demo-app-host --member=allUsers --role=roles/storage.objectViewer
gcloud storage cp web/ gs://cf-gemini-demo-app-host -r

gcloud firestore indexes composite create --collection-group=gemini-demo-images --field-config=field-path=timeStamp,order=descending --field-config=field-path=imageDescription,order=ascending



PROJECT_ID=${{secrets.PROJECT}}

PROJECT_NUMBER=$(gcloud projects list --filter="project_id:$PROJECT_ID" --format='value(project_number)')

SERVICE_ACCOUNT=$(gsutil kms serviceaccount -p $PROJECT_NUMBER)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member serviceAccount:$SERVICE_ACCOUNT \
  --role roles/pubsub.publisher
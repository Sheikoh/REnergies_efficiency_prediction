import boto3
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY_S3 = os.environ["API_KEY_S3"]
API_SECRET_KEY_S3 = os.environ["API_SECRET_KEY_S3"]

bucket_name = "renergies99-bucket"
s3_prefix = "public" 

# Liste des dossiers locaux à uploader
folders_to_upload = ["prod", "solar", "LandSat", "openweathermap"]

# Session Boto3
session = boto3.Session(
    aws_access_key_id=API_KEY_S3,
    aws_secret_access_key=API_SECRET_KEY_S3,
    region_name="eu-west-3",
)

s3 = session.resource("s3")
bucket = s3.Bucket(bucket_name)

# Tests sur les folders à uploader
for folder in folders_to_upload:
    local_folder = os.path.join("data", folder)

    if not os.path.exists(local_folder):
        print(f"Dossier introuvable : {local_folder}")
        continue

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, "data")
            s3_key = f"{s3_prefix}/{relative_path}".replace(os.sep, "/")

            print(f"Upload de {local_path} vers s3://{bucket_name}/{s3_key}")
            bucket.upload_file(local_path, s3_key)

print("Upload terminé.")

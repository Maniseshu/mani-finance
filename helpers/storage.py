@"
import boto3, uuid, os

ACC = os.getenv("R2_ACCOUNT")          # Cloudflare account ID
EP  = f"https://{ACC}.r2.cloudflarestorage.com"

s3 = boto3.client(
    "s3",
    endpoint_url=EP,
    aws_access_key_id=os.getenv("R2_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET"),
)

BUCKET = "mani-images"  # your R2 bucket name

def save_image(file_storage):
    """
    file_storage = the object you get from request.files['photo']
    Returns the unique key that you store in SQLite.
    """
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    key = f"{uuid.uuid4().hex}.{ext}"
    s3.upload_fileobj(
        file_storage,
        BUCKET,
        key,
        ExtraArgs={"ContentType": file_storage.mimetype},
    )
    return key

def public_url(key):
    """Return a full HTTPS URL you can use in <img src=...>."""
    return f"{EP}/{BUCKET}/{key}"
"@ | Set-Content -Encoding utf8 helpers\storage.py

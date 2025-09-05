import os
from prefect.blocks.system import Secret

def get_s3_settings():
    # Prefer Prefect secret block, fallback to env vars for local dev
    try:
        access_key = Secret.load("s3-access-key").get()
        secret_key = Secret.load("s3-secret-key").get()
        endpoint_url = Secret.load("s3-endpoint-url").get()
        bucket = Secret.load("s3-bucket").get()
    except Exception:
        access_key = os.environ.get("S3_ACCESS_KEY", "minioadmin")
        secret_key = os.environ.get("S3_SECRET_KEY", "minioadmin")
        endpoint_url = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
        bucket = os.environ.get("S3_BUCKET", "simulation-archives")
    return {
        "access_key": access_key,
        "secret_key": secret_key,
        "endpoint_url": endpoint_url,
        "bucket": bucket,
    }

def get_mongo_settings():
    try:
        mongo_url = Secret.load("mongo-url").get()
        db_name = Secret.load("mongo-db-name").get()
    except Exception:
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("MONGO_DB_NAME", "sim")
    return {"mongo_url": mongo_url, "db_name": db_name}

def get_redis_settings():
    try:
        redis_url = Secret.load("redis-url").get()
    except Exception:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return {"redis_url": redis_url}
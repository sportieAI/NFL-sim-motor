from config import get_s3_settings, get_mongo_settings, get_redis_settings


def print_settings():
    print("S3:", get_s3_settings())
    print("Mongo:", get_mongo_settings())
    print("Redis:", get_redis_settings())


if __name__ == "__main__":
    print_settings()

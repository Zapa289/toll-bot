import settings
from hashlib import md5

def hash_user_id(user_id: str) -> str:
    return md5(user_id.encode('utf-8')).hexdigest()

def write_to_image_cache(filename: str, datastream):
    with open(settings.IMAGE_CACHE_PATH/filename, "wb") as file:
        for chunk in datastream:
            file.write(chunk)
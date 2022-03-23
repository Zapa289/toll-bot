from settings import IMAGE_CACHE_PATH
from hashlib import md5
from os import mkdir

def hash_user_id(user_id: str) -> str:
    return md5(user_id.encode('utf-8')).hexdigest()

def write_to_image_cache(filename: str, datastream):
    if not IMAGE_CACHE_PATH.exists():
        mkdir(IMAGE_CACHE_PATH)

    with open(IMAGE_CACHE_PATH/filename, "wb") as file:
        for chunk in datastream:
            file.write(chunk)
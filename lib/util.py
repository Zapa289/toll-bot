from settings import IMAGE_CACHE_PATH
from hashlib import md5
from os import mkdir

logger = settings.base_logger.getChild(__name__)

def hash_user_id(user_id: str) -> str:
    return md5(user_id.encode('utf-8')).hexdigest()

def write_to_image_cache(filename: str, datastream):

	if not IMAGE_CACHE_PATH.exists():
		logger.warning(f"Creating image chache at {IMAGE_CAHCE_PATH}")
        mkdir(IMAGE_CACHE_PATH)    logger.info(f"Writing out image to {filename}")
    with open(settings.IMAGE_CACHE_PATH/filename, "wb") as file:
        for chunk in datastream:
            file.write(chunk)
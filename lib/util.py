import json
import fnmatch
import os
from settings import IMAGE_CACHE_PATH, IMAGE_FILE_TYPE, base_logger
from hashlib import md5
from pathlib import Path

logger = base_logger.getChild(__name__)

def find_file(prefix: str) -> str | None:
	pattern = prefix + "_*.png"
	result = []

	for _, _, files in os.walk(IMAGE_CACHE_PATH):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				result.append(name)

	if not result:
		logger.warning(f"No file found that matches prefix: {prefix}")
		return None
	if len(result) > 1:
		logger.error(f"More than one file for user: {result}")
		return None

	logger.info(f"Found file: {result[0]}")

	return result[0]

def hash_user_id(user_id: str) -> str:
	return md5(user_id.encode('utf-8')).hexdigest()

def hash_route(route: dict):
	return md5(json.dumps(route, sort_keys=True).encode('utf-8')).hexdigest()

def get_file_name(user_id) -> str:
	file_name_prefix = hash_user_id(user_id)
	return find_file(file_name_prefix)

def create_file_name(user_id: str, route: dict) -> str:
	file_name = "".join([
		hash_user_id(user_id=user_id),
		"_",
		hash_route(route),
		IMAGE_FILE_TYPE
	])
	return file_name

def write_to_image_cache(file_name: str, datastream):
	if not IMAGE_CACHE_PATH.exists():
		logger.warning(f"Creating image chache at {IMAGE_CACHE_PATH}")
		os.mkdir(IMAGE_CACHE_PATH)

	logger.info(f"Writing out image to {file_name}")
	with open(IMAGE_CACHE_PATH/file_name, "wb") as file:
		for chunk in datastream:
			file.write(chunk)

def delete_image_from_cache(file_name: str):
	file_path = Path(IMAGE_CACHE_PATH/file_name)
	try:
		os.remove(file_path)
	except FileNotFoundError:
		logger.error(f"Could not find image to delete! \"{file_path}\"")

def delete_image(user_id: str):
	file_name = get_file_name(user_id)
	delete_image_from_cache(file_name)

def save_user_route_map(user_id: str, route: dict, datastream):

	# Check for map that already exists for user
	file_name = get_file_name(user_id)
	if file_name:
		logger.warning(f"Found another file for user, deleting old file")
		logger.debug(f"Deleted image: {file_name}")
		delete_image_from_cache(file_name)

	file_name = create_file_name(user_id, route)
	write_to_image_cache(file_name=file_name, datastream=datastream)
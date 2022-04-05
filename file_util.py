import fnmatch
import json
import os
from hashlib import md5
from pathlib import Path

from settings import IMAGE_CACHE_PATH, IMAGE_FILE_TYPE, base_logger

logger = base_logger.getChild(__name__)


def find_file(prefix: str) -> list:
    """Search for files belonging to a user by matching partial filenames to the user_id hash"""
    pattern = prefix + "_*.png"
    result = []

    for _, _, files in os.walk(IMAGE_CACHE_PATH):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    return result


def hash_user_id(user_id: str) -> str:
    """Generate a hash based on user_id."""
    return hash_info(user_id)


def hash_route(route: dict):
    """Generate a hash based on the start and end address of the route."""
    hashable = json.dumps(route, sort_keys=True)
    return hash_info(hashable)


def hash_info(string: str) -> str:
    """Generate a MD5 hash of a given string"""
    return md5(string.encode("utf-8")).hexdigest()


def prune_multiple_images(files: list[str]) -> str:
    """Removes all but the newest image belonging to a user in the cache.
    Returns the filename of the newest image."""
    if len(files) <= 1:
        logger.error(f"Pruning requires more than file names: {files}")
        return None

    path_list = [Path(IMAGE_CACHE_PATH, file) for file in files]
    newest_file_path = sorted(
        [f.absolute() for f in path_list], key=os.path.getctime, reverse=True
    )[0]

    for file in files:
        if not file is newest_file_path.name:
            logger.info(f"Deleting image from cache: {file}")
            delete_image_from_cache(file)

    return newest_file_path.name


def get_file_name(user_id) -> str:
    """Search the image chache to find the image matching a user_id. If multiple files are found then the older
    images will be deleted."""
    file_name = None
    file_name_prefix = hash_user_id(user_id)

    files = find_file(file_name_prefix)

    if not files:
        logger.warning("No file found that belongs to user")
        return None
    if len(files) > 1:
        logger.error("Too many images belonging to user! Deleting old files")
        file_name = prune_multiple_images(files)
        return file_name

    file_name = files[0]
    logger.info(f"Found file: {file_name}")

    return file_name


def create_file_name(user_id: str, route: dict) -> str:
    """Create a file name based on the user_id and the start/end addresses of the route.
    All file names will be of the form {hash of user_id}_{hash of addresses}.{filetype}"""
    file_name = "".join([hash_user_id(user_id=user_id), "_", hash_route(route), IMAGE_FILE_TYPE])
    return file_name


def write_to_image_cache(file_name: str, datastream):
    """Download image from datastream."""
    if not IMAGE_CACHE_PATH.exists():
        logger.warning("Creating image chache at %s", IMAGE_CACHE_PATH)
        os.mkdir(IMAGE_CACHE_PATH)

    logger.info(f"Writing out image to {file_name}")
    with open(IMAGE_CACHE_PATH / file_name, "wb") as file:
        for chunk in datastream:
            file.write(chunk)


def delete_image_from_cache(file_name: str):
    """Delete a map image from the image cache."""
    file_path = Path(IMAGE_CACHE_PATH / file_name)
    logger.info("Deleting file %s", file_name)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        logger.error("Could not find image to delete: %s", file_path)


def delete_user_map(user_id: str):
    """Delete a map"""
    file_name = get_file_name(user_id)
    delete_image_from_cache(file_name)


def save_user_route_map(user_id: str, route: dict, datastream):
    """Take user and route information and convert to a file name.
    Download the image to the image cache."""
    # Check for map that already exists for user

    file_name = get_file_name(user_id)

    if file_name:
        logger.warning("Found another file for user, deleting old file")
        logger.debug("Deleting image: %s", file_name)
        delete_image_from_cache(file_name)

    file_name = create_file_name(user_id, route)
    write_to_image_cache(file_name=file_name, datastream=datastream)

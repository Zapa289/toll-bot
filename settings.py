import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import logging.config

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACKBOT_TOKEN = os.getenv('SLACKBOT_TOKEN')
SLACKBOT_SIGNING_SECRET = os.getenv('SLACKBOT_SIGNING_SECRET')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

IMAGE_CACHE_PATH = Path('./cache')
IMAGE_FILE_TYPE = ".png"

#IMAGE_HOST = "http://10.207.0.61:8000"
IMAGE_HOST = None

# Date storage format: 2022-03-11
RAW_DATE_FORMAT = '%Y-%m-%d'
# Date format: March 11, 2022
DATE_FORMAT = '%B %d, %Y'

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=True)
base_logger = logging.getLogger("System")
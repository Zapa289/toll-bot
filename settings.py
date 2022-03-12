import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACKBOT_TOKEN = os.getenv('SLACKBOT_TOKEN')
SLACKBOT_SIGNING_SECRET = os.getenv('SLACKBOT_SIGNING_SECRET')

# Date storage format: 2022-03-11
RAW_DATE_FORMAT = '%Y-%m-%d'
# Date format: March 11, 2022
DATE_FORMAT = '%B %d, %Y'

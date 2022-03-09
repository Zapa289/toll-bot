"""First step: Get a bot running to track days in the office"""

from slack import WebClient
from slack.errors import SlackApiError
from slack.signature.verifier import SignatureVerifier


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
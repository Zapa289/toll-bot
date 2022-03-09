from flask.wrappers import Request
from slack import WebClient
from slack.errors import SlackApiError

from slack.signature.verifier import SignatureVerifier

# client = WebClient(token=os.environ['SLACKBOT_TOKEN'])
# slack_verifier = SignatureVerifier(os.environ['SLACKBOT_SIGNING_SECRET'])

class SlackClient:

    def _init_(self, bot_token: str, signing_secret: str) -> None:
        self.client = WebClient(token=bot_token)
        self.validator = SignatureVerifier(signing_secret)

    def is_valid_request(self, event: Request) -> bool:
        """Return if event is a valid Slack request"""
        return self.validator.is_valid_request(event.get_data(), event.headers)

    def get_slack_info(self, user_id: str) -> dict[str, str]:
        """Gets information about a user from Slack"""
        user_info = {}
        try:
            user_info = self.client.users_info(user=user_id)
        except SlackApiError as error:
            error_response = error.response['error']
            print(error.response)

        if not user_info.get('ok'):
            raise UserNotFound(user_id=user_id)

        return user_info.get('user')

    def write_message(self, channel: str, message: str):
        self.client.chat_postMessage(channel=channel, text=message)

    def publish_view(client: WebClient, user_id: str, blocks: dict):
        response = client.views_publish(user_id=user_id, view=blocks)

        if not response['ok']:
            raise SlackResponseError(user_id=user_id, message=f"Error during view.publish: {response['error']}")

    def open_modal(self, trigger_id, modal):
        """Opens a modal"""
        try:
            response = self.client.views_open(trigger_id=trigger_id, view=modal)
        except SlackApiError as error:
            print(error.response)



class UserNotFound(Exception):
    """Custom exception for when Slack users_info """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.message = f"User ({self.user_id}) could not be found"
        super().__init__(self.message)

class SlackResponseError(Exception):
    """Custom exception for when Slack gives an error response"""
    def __init__(self, user_id: str, message: str = "Slack responded with an error!"):
        self.user_id = user_id
        self.message = message
        super().__init__(message)
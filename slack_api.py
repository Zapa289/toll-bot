import home

from flask.wrappers import Request
from slack import WebClient
from slack.errors import SlackApiError

from slack.signature.verifier import SignatureVerifier

from lib.user import User

class SlackClient:
    def __init__(self, signing_secret: str, bot_token:str):
        self.validator = SignatureVerifier(signing_secret=signing_secret)
        self.client = WebClient(token=bot_token)

    def is_valid_request(self, event: Request) -> bool:
        """Check if a given Slack request is valid."""
        return self.validator.is_valid_request(event.get_data(), event.headers)

    def write_message(self, channel: str, message: str):
        """Write a message to a Slack channel."""
        try:
            self.client.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            print(f"Unable to write message.\n\tSlack returned an error: {e.response['error']}")
            
    def publish_home(self, user: User):
        """Publish a user's Home tab."""
        home_blocks = home.get_home_tab(user)

        if home_blocks:
            try:
                self.publish_view(user.id, home_blocks)
            except (ValueError, SlackApiError):
                print("Error: Could not publish home tab!']")

    def publish_view(self, user_id: str, blocks: dict):
        """Publish a view to a user"""
        try:
            self.client.views_publish(user_id=user_id, view=blocks)
        except SlackApiError as e:
            print(f"Slack returned an error: {e.response['error']}")
            raise e

    def open_modal(self, trigger_id, modal):
        try:
            self.client.views_open(trigger_id=trigger_id, view=modal)
        except SlackApiError as e:
            print(f"Error: Could not open modal\n\tSlack returned an error: {e.response['error']}")
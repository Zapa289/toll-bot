"""Core function of the release bot."""
import os
import json
from pathlib import Path

from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv

from slack_client import SlackClient


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACKBOT_TOKEN = os.environ['SLACKBOT_TOKEN']
SLACKBOT_SIGNING_SECRET = os.environ['SLACKBOT_SIGNING_SECRET']

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SLACKBOT_SIGNING_SECRET, '/slack/events', app)

slack_client = SlackClient(SLACKBOT_TOKEN, SLACKBOT_SIGNING_SECRET)

@slack_event_adapter.on('app_home_opened')
def app_home_opened(payload):
    """User clicked the home tab"""
    event = payload.get('event', {})
    user_id = event.get('user')

    home_blocks = bot.get_home_tab(event)

    if home_blocks:
        slack_client.publish_view(user_id, home_blocks)

    return Response(), 200

@app.route('/actions', methods=['POST'])
def slack_action_entry():
    """Handles all actions from users"""

    if not slack_client.is_valid_request(request):
        return Response(response='Invalid request'), 200

    event = json.loads(request.form['payload'])

    response = bot.process_event(event)

    return Response(response=response), 200

def main():
    """Start the bot"""
    app.run(debug=True)

if __name__ == "__main__":
    main()

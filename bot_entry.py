import os
import json
import toll_bot
from db_manager import SQLiteDatabaseAccess
from pathlib import Path
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
from lib.user import UserManager
from slack_api import SlackClient

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACKBOT_TOKEN = os.getenv('SLACKBOT_TOKEN')
SLACKBOT_SIGNING_SECRET = os.getenv('SLACKBOT_SIGNING_SECRET')

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SLACKBOT_SIGNING_SECRET, '/slack/events', app)

slack_client = SlackClient(bot_token=SLACKBOT_TOKEN, signing_secret=SLACKBOT_SIGNING_SECRET)

db = SQLiteDatabaseAccess('test.db')
user_manager = UserManager(db)

@slack_event_adapter.on('app_home_opened')
def app_home_opened(payload):
    """User clicked the home tab"""
    event = payload.get('event', {})
    user_id = event.get('user')
    user = user_manager.new_user(user_id=user_id)
    slack_client.publish_home(user)

@app.route('/actions', methods=['POST'])
def slack_action_entry():
    """Handles all actions from users"""

    if not slack_client.is_valid_request(request):
        return jsonify(text="Invalid request")

    payload = json.loads(request.form['payload'])

    toll_bot.process_action(payload)
    return {}#jsonify(response)

def main():
    """Start the bot"""
    app.run(debug=True)

if __name__ == "__main__":
    main()

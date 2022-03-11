import settings
from toll_bot import TollBot
from db_manager import SQLiteDatabaseAccess

from flask import Flask, request, jsonify
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

app = Flask(__name__)

bolt_app = App(token=settings.SLACKBOT_TOKEN, signing_secret=settings.SLACKBOT_SIGNING_SECRET)

bot = TollBot(SQLiteDatabaseAccess('test.db'))

@bolt_app.event('app_home_opened')
def app_home_opened(client: WebClient, event, logger):
    """User clicked the home tab"""

    user_id = event.get('user')
    home_tab = bot.home_tab(user_id)
    client.views_publish(user_id=user_id, view=home_tab)

@bolt_app.action('addDate')
def add_date(payload: dict, say: Say):
    date = None
    bot.add_date(payload['user'], date)

handler = SlackRequestHandler(bolt_app)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request and dispatch method of App """
    return handler.handle(request)

def main():
    """Start the bot"""
    app.run(debug=True)

if __name__ == "__main__":
    main()

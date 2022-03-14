import settings
import re
from toll_bot import TollBot
from db_manager import SQLiteDatabaseAccess

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from datetime import datetime

app = Flask(__name__)

bolt_app = App(token=settings.SLACKBOT_TOKEN, signing_secret=settings.SLACKBOT_SIGNING_SECRET)

bot = TollBot(SQLiteDatabaseAccess('test.db'))

def publish_home_tab(client: WebClient, user_id):
    home_tab = bot.home_tab(user_id)
    client.views_publish(user_id=user_id, view=home_tab)

@bolt_app.event('app_home_opened')
def app_home_opened(client: WebClient, event, logger):
    """User clicked the home tab"""

    user_id = event.get('user')
    publish_home_tab(client, user_id)

@bolt_app.action('addDate')
def add_date(ack, client: WebClient, context, body):
    ack()

    # Find the current state of the datepicker
    date_raw = body['view']['state']['values']['DateBlock']['DatePicker']['selected_date']
    # None means datepicker has been left as default, use today's date
    date = date_raw if date_raw else datetime.today().strftime(settings.RAW_DATE_FORMAT)

    user_id = context['user_id']
    bot.add_user_date(user_id, date)
    publish_home_tab(client, user_id)

@bolt_app.action(re.compile('date_menu_\d'))
def date_menu(ack, client, payload, body, context):
    ack()

    user_id = context['user_id']

    if payload["selected_option"]["value"] == "remove_date":
        for block in body['view']['blocks']:
            if block['block_id'] == payload['block_id']:
                date = block['text']['text']
        bot.delete_user_date(user_id, date)
        publish_home_tab(client, user_id)

@bolt_app.action("DatePicker")
def date_picker(ack):
    ack()

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

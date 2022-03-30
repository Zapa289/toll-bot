import logging
import re
from datetime import date, datetime

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import home
import settings
from db_manager import SQLiteDatabaseAccess
from toll_bot import TollBot

app = Flask(__name__)

bolt_app = App(
    token=settings.SLACKBOT_TOKEN, signing_secret=settings.SLACKBOT_SIGNING_SECRET
)

bot = TollBot(SQLiteDatabaseAccess("test.db"))


def publish_home_tab(client: WebClient, user_id):

    home_tab = bot.home_tab(user_id)

    logging.info(f"Publishing home tab for User {user_id}")

    try:
        client.views_publish(user_id=user_id, view=home_tab)
    except SlackApiError as e:
        logging.error(f"Could not publish view: {e}")
        logging.debug(f"View: {home_tab}")


def get_selected_overflow_value(payload):
    """Returns the selected option from an overflow menu"""
    return payload["selected_option"]["value"]


def get_view_block_list(body):
    """Returns list of blocks in current view"""
    return body["view"]["blocks"]


@bolt_app.event("app_home_opened")
def app_home_opened(client: WebClient, event):
    """User clicked the home tab"""
    user_id = event.get("user")
    logging.info(f"User {user_id} opened home tab")
    publish_home_tab(client, user_id)


@bolt_app.action("addDate")
def add_date(ack, client: WebClient, context, body):
    ack()

    # Find the current state of the datepicker. Location of the datepicker
    # is as laid out in home.make_home_blocks()
    current_state = body["view"]["state"]["values"]
    input_date = current_state["DateBlock"]["DatePicker"]["selected_date"]

    # None means datepicker has been left as default, use today's date
    new_date = date.fromisoformat(input_date) if input_date else date.today()
    user_id = context["user_id"]

    logging.info(f'Adding new date "{new_date}" to User {user_id}')

    bot.add_user_date(user_id, new_date)
    publish_home_tab(client, user_id)


@bolt_app.action(re.compile("date_menu_\d"))
def date_menu(ack, client, payload, body, context):
    ack()

    user_id = context["user_id"]

    if get_selected_overflow_value(payload) == "remove_date":
        for block in get_view_block_list(body):
            if block["block_id"] == payload["block_id"]:
                raw_date = block["text"]["text"]

        selected_date = datetime.strptime(raw_date, settings.DATE_FORMAT).date()

        logging.info(f'Removing date "{selected_date}" from User {user_id}')

        bot.delete_user_date(user_id, selected_date)
        publish_home_tab(client, user_id)


@bolt_app.action("DatePicker")
def date_picker(ack):
    ack()


@bolt_app.action("EnterAddress")
def enter_address(ack, client: WebClient, body):
    ack()
    trigger_id = body["trigger_id"]
    address_modal = home.get_address_modal()

    logging.info("User hit Enter Address")

    response = client.views_open(view=address_modal, trigger_id=trigger_id)


@bolt_app.view("address-modal")
def handle_address_modal(ack, view, context, client: WebClient):
    ack()
    modal_state = view["state"]["values"]

    starting_address = modal_state["AddressInput"]["AddressInput"]["value"]
    campus_selection = modal_state["CampusInput"]["CampusSelection"]["selected_option"][
        "value"
    ]

    user_id = context["user_id"]

    logging.info(f"User {user_id} submitted address modal")

    bot.handle_address_update(user_id, starting_address, campus_selection)
    try:
        publish_home_tab(client, user_id)
    except SlackApiError:
        logging.error("Slack reported an error", exc_info=True)


@bolt_app.action("DeleteRoute")
def handle_address_modal(ack, context, client: WebClient):
    ack()

    user_id = context["user_id"]

    logging.info(f"Delete Route for User {user_id}")

    bot.handle_delete_route(user_id)
    try:
        publish_home_tab(client, user_id)
    except SlackApiError:
        logging.error("Slack reported an error", exc_info=True)


###########################
handler = SlackRequestHandler(bolt_app)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Declaring the route where slack will post a request and dispatch method of App"""
    return handler.handle(request)


def main():
    """Start the bot"""
    app.run(debug=True)


if __name__ == "__main__":
    main()

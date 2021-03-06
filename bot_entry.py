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

bolt_app = App(token=settings.SLACKBOT_TOKEN, signing_secret=settings.SLACKBOT_SIGNING_SECRET)

bot = TollBot(SQLiteDatabaseAccess("test.db"))


def publish_home_tab(client: WebClient, user_id):
    """Publish a user's home tab"""
    home_tab = bot.home_tab(user_id)

    logging.info("Publishing home tab for User %s", user_id)

    try:
        client.views_publish(user_id=user_id, view=home_tab)
    except SlackApiError as error:
        logging.error("Could not publish view: %s", error)
        logging.debug("View: %s", home_tab)


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
    logging.info("User %s opened home tab", user_id)
    publish_home_tab(client, user_id)


@bolt_app.action("addDate")
def add_date(ack, client: WebClient, context, body):
    """User clicked Add Date. Grab the current value of the datepicker
    and add that date to the user and database."""
    ack()
    # Find the current state of the datepicker. Location of the datepicker
    # is as laid out in home.make_home_blocks()

    current_state = body["view"]["state"]["values"]
    input_date = current_state["DateBlock"]["DatePicker"]["selected_date"]

    # None means datepicker has been left as default, use today's date
    new_date = date.fromisoformat(input_date) if input_date else date.today()
    user_id = context["user_id"]

    logging.info('Adding new date "%s" to User %s', new_date, user_id)

    bot.add_user_date(user_id, new_date)
    publish_home_tab(client, user_id)


@bolt_app.action(re.compile(r"date_menu_\d"))
def date_menu(ack, client, payload, body, context):
    """User has selected an option in a date blocks overflow menu. Process the given action."""
    ack()

    user_id = context["user_id"]

    if get_selected_overflow_value(payload) == "remove_date":
        for block in get_view_block_list(body):
            if block["block_id"] == payload["block_id"]:
                raw_date = block["text"]["text"]

        selected_date = datetime.strptime(raw_date, settings.DATE_FORMAT).date()

        logging.info('Removing date "%s" from User %s', selected_date, user_id)

        bot.delete_user_date(user_id, selected_date)
        publish_home_tab(client, user_id)


@bolt_app.action("DatePicker")
def date_picker(ack):
    """Stub for modifying the datepicker. Only care about the datepicker
    once the user selects Add Date."""
    ack()


@bolt_app.action("EnterAddress")
def enter_address(ack, client: WebClient, body):
    """User selected Enter Address so serve up the address modal."""
    ack()
    trigger_id = body["trigger_id"]
    address_modal = home.get_address_modal()

    logging.info("User hit Enter Address")

    client.views_open(view=address_modal, trigger_id=trigger_id)


@bolt_app.view("address-modal")
def handle_address_modal(ack, view, context, client: WebClient):
    """User has submitted the address modal so crunch that into
    a static map to display to the user."""
    ack()
    modal_state = view["state"]["values"]

    starting_address = modal_state["AddressInput"]["AddressInput"]["value"]
    campus_selection = modal_state["CampusInput"]["CampusSelection"]["selected_option"]["value"]

    user_id = context["user_id"]

    logging.info("User %s submitted address modal", user_id)

    bot.handle_address_update(user_id, starting_address, campus_selection)
    try:
        publish_home_tab(client, user_id)
    except SlackApiError:
        logging.error("Slack reported an error", exc_info=True)


@bolt_app.action("DeleteRoute")
def handle_delete_route(ack, context, client: WebClient):
    """User selected Delete Route. Delete static map from image cache and republish the home tab."""
    ack()

    user_id = context["user_id"]

    logging.info("Delete Route for User %s", user_id)

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

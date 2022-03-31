from datetime import date
from pathlib import Path

from slack_sdk.models.blocks.basic_components import (
    ConfirmObject,
    MarkdownTextObject,
    Option,
    PlainTextObject,
)
from slack_sdk.models.blocks.block_elements import (
    ButtonElement,
    DatePickerElement,
    OverflowMenuElement,
    PlainTextInputElement,
    StaticSelectElement,
)
from slack_sdk.models.blocks.blocks import (
    ActionsBlock,
    Block,
    ContextBlock,
    DividerBlock,
    HeaderBlock,
    ImageBlock,
    InputBlock,
    SectionBlock,
)
from slack_sdk.models.views import View

import settings
from file_util import get_file_name
from offices import OFFICE_LIST
from user import User

logger = settings.base_logger.getChild(__name__)


def get_home_tab(user: User) -> View:
    """Generate the Home tab for a user"""
    logger.info(f"Creating home tab for User {user.id}")
    home_tab = View(type="home", blocks=make_home_blocks(user))

    return home_tab


def make_home_blocks(user: User) -> list[Block]:
    """Create all the blocks cooresponding to a home View"""
    home_blocks: list[Block] = []

    home_blocks.extend(get_map_blocks(user=user))
    home_blocks.append(DividerBlock())
    home_blocks.append(HeaderBlock(text="Dates in the office"))
    home_blocks.extend(get_datepicker_blocks())
    home_blocks.extend(get_date_blocks(user))

    return home_blocks


def get_dates(user: User) -> list[Block]:
    """Get all the slack blocks for dates belonging to user"""
    date_blocks: list[Block] = []

    logger.info("Creating date blocks")

    for num, this_date in enumerate(user.dates):
        date_text = this_date.strftime(settings.DATE_FORMAT)
        date_blocks.append(
            SectionBlock(
                block_id=f"date_{num}",
                text=date_text,
                accessory=OverflowMenuElement(
                    action_id=f"date_menu_{num}",
                    options=[
                        Option(label="Remove date", value="remove_date"),
                        Option(label="Something", value="something"),
                    ],
                ),
            )
        )
    if not date_blocks:
        logger.info("No tracked dates, creating context block")
        date_blocks = [
            ContextBlock(elements=[PlainTextObject(text="You do not have any tracked dates")])
        ]

    return date_blocks


def get_date_blocks(user: User) -> list[Block]:
    """Create blocks for all of the dates tracked by a user."""
    date_blocks = []
    date_blocks.extend(get_dates(user))
    return date_blocks


def get_datepicker_blocks() -> list[Block]:
    """Create the datepicker block"""
    today = date.today().strftime(settings.DATE_FORMAT)
    return [
        ActionsBlock(
            block_id="DateBlock",
            elements=[
                DatePickerElement(action_id="DatePicker", placeholder=f"{today}"),
                ButtonElement(text="Add Date", action_id="addDate", value="AddDate"),
            ],
        )
    ]


def get_map_blocks(user: User) -> list[Block]:
    """Create the blocks for the static map. Searches the image cache for a
    map belonging to the user to serve up. If there is no map cached for
    the user then a button that prompts the user to enter an address will
    be created."""

    map_blocks: list[Block] = []
    image_name = get_file_name(user.id)

    logger.info("Create map blocks")
    logger.debug(f"Expected map image name: {image_name}")

    if not image_name or not Path(settings.IMAGE_CACHE_PATH / image_name).is_file():
        logger.info("No cached map found for user; Provide the Enter Address button")
        map_blocks.append(
            ActionsBlock(
                block_id="MapBlock",
                elements=[
                    ButtonElement(
                        text="Enter starting address",
                        action_id="EnterAddress",
                        value="EnterAddress",
                        style="primary",
                    )
                ],
            )
        )
        return map_blocks

    logger.info("Found cached map for user")

    if not settings.IMAGE_HOST:
        logger.warning("No image host configured. Images cannot be displayed")
        return [
            ContextBlock(
                elements=[
                    PlainTextObject(text="Route information unavailable, no image host configured")
                ]
            )
        ]

    logger.info("Create image block")
    url = settings.IMAGE_HOST + image_name
    logger.debug(f"Image URL: {url}")
    map_blocks.append(HeaderBlock(text="Your route to work"))
    map_blocks.append(ImageBlock(image_url=url, alt_text="Your route to work"))
    map_blocks.append(
        ActionsBlock(
            block_id="MapBlock",
            elements=[
                ButtonElement(
                    text="Delete Route",
                    action_id="DeleteRoute",
                    value="DeleteRoute",
                    style="danger",
                    confirm=ConfirmObject(
                        title="Confirm Delete Route",
                        text="Are you sure you want to delete your route? This cannot be undone.",
                        deny="Cancel",
                        style="danger",
                    ),
                ),
            ],
        )
    )

    return map_blocks


#
# Modals
#
def get_campus_options() -> list[Option]:
    """Returns a list of Slack Options for the available campuses"""
    office_options: list[Option] = []

    for office in OFFICE_LIST:
        option = Option(
            value=office.label,
            label=office.label,
            text=office.label + f" ({office.address})",
        )
        office_options.append(option)
    return office_options


def get_address_modal() -> View:
    """Generate the address input modal"""
    address_modal = View(
        type="modal",
        title="Toll Mapper",
        callback_id="address-modal",
        submit="Submit",
        close="Cancel",
        blocks=[
            SectionBlock(
                text=MarkdownTextObject(
                    text="You can enter your address to get an approximate amount spent on tolls going to and from campus."
                    " Make sure your address is able to be found with <https://www.google.com/maps|Google Maps>."
                    "\n\nYou can modify this address in the future, but *please try to limit changes* as API calls"
                    " are not limitless."
                )
            ),
            InputBlock(
                label="Starting Address",
                element=PlainTextInputElement(
                    placeholder="Starting Address",
                    action_id="AddressInput",
                ),
                block_id="AddressInput",
            ),
            InputBlock(
                block_id="CampusInput",
                label="HPE Office",
                element=StaticSelectElement(
                    placeholder="Select an HPE Campus",
                    action_id="CampusSelection",
                    options=get_campus_options(),
                ),
            ),
        ],
    )
    return address_modal

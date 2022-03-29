import settings
from pathlib import Path
from offices import OFFICE_LIST
from lib.user import User
from datetime import date
from lib.util import hash_user_id
from slack_sdk.models.views import View
from slack_sdk.models.blocks.blocks import Block, SectionBlock, ActionsBlock, DividerBlock, HeaderBlock, ContextBlock, InputBlock, ImageBlock
from slack_sdk.models.blocks.block_elements import DatePickerElement, ButtonElement, OverflowMenuElement, PlainTextInputElement, StaticSelectElement
from slack_sdk.models.blocks.basic_components import Option, PlainTextObject, MarkdownTextObject

def make_home_blocks(user: User) -> list[Block]:

    home_blocks: list[Block] = []

    home_blocks.extend(get_map_blocks(user=user))
    home_blocks.append(DividerBlock())
    home_blocks.extend(get_datepicker_blocks())
    home_blocks.append(DividerBlock())
    home_blocks.extend(get_date_blocks(user))

    return home_blocks

def get_home_tab(user: User) -> View:
    """Generate the Home tab for a user"""

    home_tab = View(
        type="home",
        blocks=make_home_blocks(user)
    )

    return home_tab

def get_dates(user: User) -> list[Block]:
    """Get all the slack blocks for dates belonging to user"""
    date_blocks: list[Block] = []

    for num, this_date in enumerate(user.dates):
        date_text = this_date.strftime(settings.DATE_FORMAT)
        date_blocks.append(
            SectionBlock(block_id=f"date_{num}", text=date_text,
                accessory=OverflowMenuElement(action_id=f"date_menu_{num}", options=[
                    Option(label="Remove date", value="remove_date"),
                    Option(label="Something", value="something")
                ])
            )
        )
    if not date_blocks:
        date_blocks = [ContextBlock(elements=[PlainTextObject(text="You do not have any tracked dates")])]

    return date_blocks

def get_date_blocks(user: User) -> list[Block]:
    date_blocks = [HeaderBlock(text="Dates in the office")]
    date_blocks.extend(get_dates(user))
    return date_blocks

def get_datepicker_blocks() -> list[Block]:
    today = date.today().strftime(settings.DATE_FORMAT)
    return [
        SectionBlock(text={"type": "mrkdwn", "text": f"*{today}*"}),
        ActionsBlock(block_id="DateBlock", elements=[
            DatePickerElement(action_id="DatePicker", placeholder="Use today's date"),
            ButtonElement(text="Add Date", action_id="addDate", value="AddDate")
            ]
        )
    ]

def get_map_blocks(user: User) -> list[Block]:
    map_blocks : list[Block] = []
    image_name = hash_user_id(user.id) + settings.IMAGE_FILE_TYPE

    if not Path(settings.IMAGE_CACHE_PATH/image_name).is_file():
        map_blocks.append(
            ActionsBlock(block_id="MapBlock", elements=[
                ButtonElement(text="Enter starting address", action_id="EnterAddress", value="EnterAddress")
                ])
        )
    else:
        url = settings.IMAGE_HOST + "/" + image_name
        print(url)
        map_blocks.append(
            ImageBlock(
                image_url=url,
                alt_text="Your route to work"
            )
        )

    return map_blocks

#
# Modals
#
def get_campus_options() -> list[Option]:
    """Returns a list of Slack Options for the available campuses"""
    office_options : list[Option] = []

    for office in OFFICE_LIST:
        option = Option(
            value=office.label,
            label=office.label,
            text=office.label + f" ({office.address})"
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
                element= PlainTextInputElement(
                    placeholder="Starting Address",
                    action_id="AddressInput",
                ),
                block_id="AddressInput"
            ),
            InputBlock(
                block_id="CampusInput",
                label="HPE Office",
                element= StaticSelectElement(
                    placeholder="Select an HPE Campus",
                    action_id= "CampusSelection",
                    options= get_campus_options()
                )
            )
        ]
    )

    return address_modal

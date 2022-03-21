import settings
from lib.user import User
from datetime import date
from slack_sdk.models.views import View
from slack_sdk.models.blocks.blocks import Block, SectionBlock, ActionsBlock, DividerBlock, HeaderBlock, ContextBlock
from slack_sdk.models.blocks.block_elements import DatePickerElement, ButtonElement, OverflowMenuElement
from slack_sdk.models.blocks.basic_components import Option, PlainTextObject

def make_home_blocks(user: User) -> list[Block]:
    today = date.today().strftime(settings.DATE_FORMAT)
    home_blocks: list[Block] = [
        SectionBlock(type="section", text={"type": "mrkdwn", "text": f"*{today}*"}),
        ActionsBlock(block_id="DateBlock", elements=[
            DatePickerElement(action_id="DatePicker", placeholder="Use today's date"),
            ButtonElement(text="Add Date", action_id="addDate", value="AddDate")
        ]),
        DividerBlock(),
        HeaderBlock(text="Dates in the office")
    ]

    home_blocks.extend(get_dates(user))

    return home_blocks

def get_home_tab(user: User) -> View:
    """Generate the Home tab for a user"""

    home_tab = View(
        type="home",
        blocks=make_home_blocks(user)
    )

    return home_tab

def get_dates(user: User) -> list[Block]:
    """Get all the slack blocks for different """
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

#
# Modals
#



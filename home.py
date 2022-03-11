from lib.user import User
from datetime import date
from slack_sdk.models.views import View
from slack_sdk.models.blocks.blocks import Block, SectionBlock, ActionsBlock, DividerBlock, HeaderBlock, ContextBlock
from slack_sdk.models.blocks.block_elements import DatePickerElement, ButtonElement, OverflowMenuElement
from slack_sdk.models.blocks.basic_components import Option, PlainTextObject

def make_home_blocks(user: User) -> list[Block]:
    today = date.today().strftime('%B %d, %Y')
    home_blocks: list[Block] = []

    home_blocks.extend([
        SectionBlock(type="section", text={"type": "mrkdwn", "text": f"*{today}*"}),
        ActionsBlock(elements=[
            DatePickerElement(placeholder="Use today's date"),
            ButtonElement(text="Add Date", action_id="addDate", value="AddDate")
        ]),
        DividerBlock(),
        HeaderBlock(text="Dates in the office")
    ])
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
    
    for date in user.dates:
        date_blocks.append(
            SectionBlock(text=date,
                accessory=OverflowMenuElement(options=[
                    Option(text="View Event Details", value="view_event_details"),
                    Option(text="Another thing to do", value="another_thing")
                ])
            )
        )

    if not date_blocks:
        date_blocks = ContextBlock(elements=[PlainTextObject(text="You do not have any tracked dates")])
    
    return date_blocks

#
# Modals
#



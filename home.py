import json
from lib.user import User
from datetime import date

def get_home_tab(user: User) -> str:
    """Generate the Home tab for a user"""

    date_blocks: list = get_dates(user)

    home_tab = \
    {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{date.today().strftime('%B %d, %Y')}*"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "datepicker",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Today",
                            "emoji": True
                        }
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Add Date",
                            "emoji": True
                        },
                        "value": "AddDate",
                        "action_id": "addDate"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Dates in the office",
                    "emoji": True
                }
            },
            date_blocks
        ]
    }
    return json.dumps(home_tab)

def get_dates(user: User) -> list:
    """Get all the slack blocks for different """
    date_blocks: list[str] = []

    for date in user.dates:
        block = \
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{date}"
            },
            "accessory": {
                "type": "overflow",
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "View Event Details",
                            "emoji": True
                        },
                        "value": "view_event_details"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Change Response",
                            "emoji": True
                        },
                        "value": "change_response"
                    }
                ]
            }
        }
        date_blocks.append(block)

    if not date_blocks:
        date_blocks = \
        {
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "You do not have any tracked dates.",
					"emoji": True
				}
			]
		}
    return date_blocks

#
# Modals
#



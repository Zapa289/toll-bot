"""First step: Get a bot running to track days in the office"""

def process_action(payload):
    actions = payload['actions']

    for action in actions:
        action_id = action['action_id']
        if action_id in ACTIONS:
            ACTIONS[action_id](action)

def add_date(action):
    print("Let's add a new date...")

OK_RESPONSE = {
    "ok" : True
}

ACTIONS = {
    "addDate" : add_date
}
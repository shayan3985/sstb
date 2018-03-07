import json


class MessageHelper:
    def __init__(self):
        with open('staticJson', 'r') as f:
            self.json = json.loads(f.read())

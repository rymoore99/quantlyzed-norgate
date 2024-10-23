import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv, find_dotenv
import sentry_sdk
from sentry_sdk import capture_exception

load_dotenv(find_dotenv()) # Load the .env file

class SlackSender:

    # def __init__(self):

    def post_message(self, msg):
        # trading slack app api key
        client = WebClient(token=os.environ['SLACK_TOKEN'])

        # trading channel
        channel_id = 'C01JF1CFPHR'

        try:
            # Call the conversations.list method using the WebClient
            result = client.chat_postMessage(
                channel=channel_id,
                text=msg
                # You could also use a blocks[] array to send richer content
            )
            # Print result, which includes information about the message (like TS)
            #print(result)

        except SlackApiError as e:
            print(f"Error: {e}")


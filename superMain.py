# -*- coding: utf-8 -*-
from flask import Flask, request, make_response
from slacker import Slacker
import websocket
import json

def abc(text):
    return text

def _event_handler(event_type, slack):
    print(slack["event"])
    if event_type == "app_mention":
        channel = slack["event"]["channel"]
        text = slack["event"]["text"]
        keywords = abc(text)
        slack.chat.post_message('#general', keywords)


def run():
    slack = Slacker("xoxb-502213453520-507384248019-BsMUDahN9t0xkAgG9nUKIkB9")
    res = slack.rtm.connect()
    endpoint = res.body['url']
    print('!')
    ws = websocket.create_connection(endpoint)
    ws.settimeout(60)
    while True:
        try:
            slack_event = json.loads(ws.recv())
            print(slack_event)
            if "challenge" in slack_event:
                print("Hi!")
            if "event" in slack_event:
                event_type = slack_event["event"]["type"]
                _event_handler(event_type, slack_event)

        except websocket.WebSocketTimeoutException:
            ws.send(json.dumps({'type': 'ping'}))

        except websocket.WebSocketConnectionClosedException:
            print("Connection closed")
            break

        except Exception as e:
            print(e)
            break

    ws.close()

while True:
    run()



# # userList 출력
# response = slack.users.list()
# print(response.body['members'])
# users = response.body['members']
# for user in users :
#     print(user['profile']['real_name'])

# # channel List 출력
# response = slack.channels.list()
# channels = response.body['channels']
# print(channels)

'''

슬랙 봇 프로젝트

> 구조 :
                        ┏ 파이썬 코드 ┓
    이벤트(호출) ┬ request - 처리 - Slacker - 출력
    일반 입력    ┘

> 이벤트
    slack의 event api 사용
    hear() 함수에서 처리

> 텍스트 입력

출력 : Slacker

'''
# -*- coding: utf-8 -*-
import json
from flask import Flask, request, make_response
from slacker import Slacker
import websocket
import re
from threading import Thread

app = Flask(__name__)

slack_token = "xoxb-502213453520-507384248019-BsMUDahN9t0xkAgG9nUKIkB9"
slack_client_id = "502213453520.507688847685"
slack_client_secret = "c667f791180fb05ddf7fdf5dccfad9c2"
slack_verification = "9raU6TJb1GWVDcrpnioHiCPW"
slack = Slacker(slack_token)
res = slack.rtm.connect()
endpoint = res.body['url']

chat = {}

def get_chat(chat):
    ws = websocket.connect(endpoint)
    while True:
        msg = json.loads(ws.recv())
        print(msg)

p = Thread(target=get_chat, args=(chat))

def get_answer(event):
    ws = websocket.connect(endpoint)
    while True:
        msg = json.loads(ws.recv())
        if 'user' in msg and 'text' in msg:
            if event['user'] == msg['user']:
                re_yes = re.compile('((yes))|(응)', re.I)
                re_no = re.compile('((no)|(아니))', re.I)
                if re_yes.match(msg['text']):
                    slack.chat.post_message(event["channel"], "안녕하세요, 000님")
                    break;
                elif re_no.match(msg['text']):
                    slack.chat.post_message(event["channel"], "필요할때 불러주세요, 000님")
                    break;
                else:
                    slack.chat.post_message(event["channel"], "`응` / `아니`로 대답해주세요")

# 함수 구현하기
def call_elice(text, event):
    # 여기에 함수를 구현해봅시다.
    keywords = []
    res = slack.rtm.connect()
    endpoint = res.body['url']
    ws = websocket.create_connection(endpoint)
    ws.settimeout(60)
    while True:
        try:
            slack.chat.post_message(event['channel'], "부르셨어요? \n `응` / `아니`")
            get_answer(event)

        except websocket.WebSocketTimeoutException:
            ws.send(json.dumps({'type': 'ping'}))

        except websocket.WebSocketConnectionClosedException:
            print("Connection closed")
            break

        except Exception as e:
            print(e)
            break

    ws.close()
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_response):
    print(slack_response["event"])
    if event_type == "app_mention":
        channel = slack_response["event"]["channel"]
        text = slack_response["event"]["text"]
        slack.chat.post_message(channel, "부르셨어요? \n `응` / `아니`")

        call_elice(text, slack_response["event"])

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/event", methods=["GET", "POST"])
def hears():
    slack_response = json.loads(request.data)

    if "challenge" in slack_response:
        return make_response(slack_response["challenge"], 200, {"content_type":"application/json"})

    if slack_verification != slack_response.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_response["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    # 쓰레드
    if "event" in slack_response:
        event_type = slack_response["event"]["type"]
        return _event_handler(event_type, slack_response)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)

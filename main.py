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

caller = []
channel_list = []

def get_name(id):
    user = slack.users.info(id)
    print(user)
    name = user.body["user"]["name"]
    return name


def check_user(event, msg):
    if 'user' in msg and 'text' in msg:
        if event['user'] == msg['user']:
            return True
    return False

def elice(ws, event, msg):
    name = get_name(msg['user'])
    channel = event["channel"]
    slack.chat.post_message(channel, "뭐가 필요하신가요?\n `너 누구니?` / `맞춤법검사해줘` / `문법경찰출동`".format(name))
    while True:
        msg = json.loads(ws.recv())
        if check_user(event, msg):
            msg = msg['text']
            msg = msg.replace(' ', '').strip()
            if msg == '<@UEXBA7A0K>':
                continue
            elif '누구' in msg:
                who_is_elice(channel)
            elif '검사' in msg:
                lets_check(channel)
            elif '경찰' in msg:
                police(channel)
            elif '잘가' in msg:
                break;
            else:
                slack.chat.post_message(channel, "다시 말해주세요")
                slack.chat.post_message(channel,
                                        "뭐가 필요하신가요?\n `너 누구니?` / `맞춤법검사해줘` / `문법경찰출동`".format(name))

def who_is_elice(channel):
    slack.chat.post_message(channel, "저는...")


def lets_check(channel):
    slack.chat.post_message(channel, "입력 방법은...")


def police(channel):
    slack.chat.post_message(channel, "경찰 출동!")


# 함수 구현하기
def call_elice(event):
    slack.chat.post_message(event['channel'], "부르셨어요? \n `응` / `아니`")
    res = slack.rtm.connect()
    endpoint = res.body['url']
    ws = websocket.create_connection(endpoint)
    while True:
        msg = json.loads(ws.recv())
        print(msg)
        if check_user(event, msg):
            name = get_name(msg['user'])
            channel = event["channel"]
            re_yes = re.compile('((yes))|(응)|(ㅇ)+', re.I)
            re_no = re.compile('((no)|(아니))|(ㄴ)+', re.I)
            if msg['text'] == '<@UEXBA7A0K>':
                continue
            elif re_yes.match(msg['text']):
                slack.chat.post_message(channel, "안녕하세요!".format(name))
                elice(ws, event, msg)
                break;
            elif re_no.match(msg['text']):
                slack.chat.post_message(channel, "필요할때 불러주세요".format(name))
                break;

            else:
                slack.chat.post_message(channel, "`응` / `아니`로 대답해주세요")
    ws.close()


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_response):
    global caller, channel_list
    print(slack_response["event"])
    if event_type == "app_mention":
        channel = slack_response["event"]["channel"]
        if slack_response["event"]["channel"] in channel_list:
            slack.chat.post_message(channel, "저 여기 있어요~")
        caller.append(slack_response)
        channel_list.append(channel)
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


def proc(slack_response):
    call_elice(slack_response["event"])


def interact():
    while True:
        if len(caller) > 0:
            res = caller.pop()
            proc(res)
            channel_list.remove(res["event"]["channel"])


if __name__ == '__main__':
    p = Thread(target=interact)
    p.start()
    app.run('127.0.0.1', port=5000)

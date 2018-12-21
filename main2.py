# -*- coding: utf-8 -*-
import json
import urllib.request
import slacker_test

from bs4 import BeautifulSoup
from flask import Flask, request, make_response
from slackclient import SlackClient

app = Flask(__name__)

slack_token = "xoxb-502213453520-507384248019-BsMUDahN9t0xkAgG9nUKIkB9"
slack_client_id = "502213453520.507688847685"
slack_client_secret = "c667f791180fb05ddf7fdf5dccfad9c2"
slack_verification = "9raU6TJb1GWVDcrpnioHiCPW"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    # 여기에 함수를 구현해봅시다.
    url = "https://www.youtube.com/feed/trending"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    keywords = []

    if "유튜브" in text:
        keywords = ["유튭 Top 5\n"]
        datas = []
        for i, row in enumerate(soup.find_all("div", class_="yt-lockup-content")):
            title = row.find("a", class_="yt-uix-tile-link").get_text().strip()
            views = row.find("ul", class_="yt-lockup-meta-info").get_text().strip()
            title = title if len(title) < 20 else title[:20]+"..."
            views = views.strip().split()[-1]
            datas.append([title, views])
        datas.sort(key = lambda d: d[1], reverse = True)
        for i in range(5):
            keywords.append("{}위 : {} / 조회수 : {}".format(i+1, datas[i][0], datas[i][1]))
            # if i< 5:
            #     tt = title.get_text().strip()
            #     keywords.append("> {}".format(tt if len(tt) < 20 else tt[:17]+'...'))

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)

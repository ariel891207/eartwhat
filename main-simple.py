# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 09:58:19 2023

@author: sarie
"""

import json
import random
import csv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FlexSendMessage, TextMessage, LocationMessage, TextSendMessage, QuickReplyButton, QuickReply, LocationAction, PostbackEvent


channel_token  = "e6cHLmikmRMXrpIuxPtDFc38SVGPxX+53Dq0K8bTZgssW5X5+ZF+ZoLm7BK/PcwzCqUjEpk6Q0XCEzAyjfkz4m1gR6aFNUSTbZc1aKeHzXlzqD1u6G8zWjW1/dv302GbpeTIsJbkntL0yYPuS3TuZQdB04t89/1O/w1cDnyilFU="
channel_secret = "88ff97bca97347f2ed2064bcf8c2f130"


app = Flask(__name__)
line_bot_api = LineBotApi(channel_token)
handler = WebhookHandler(channel_secret)
#附近店家
def fixed_position(latitude, longitude):
    contents={}
    contents['type']='carousel'
    bubbles=[]
    with open('Restaurant.csv', 'r', encoding="utf-8") as csvfile:
        csvr = csv.reader(csvfile)
        for i in csvr:
            name = i[1]
            dec = i[2]
            add = i[3]
            tel = i[7]
            time = i[8]
            photo = i[10]
            px = float(i[16])
            py = float(i[17])
            if dec == "":
                dec = "無資料!"
            elif len(dec) > 300:
                dec = dec[:250]
                dec += "\n\n--字數過多以下省略--" 
            elif tel == "":
                tel ="無資料!"
            elif time == "":
                time ="無資料!"
            elif photo == "":
                photo = "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png"
            if abs(latitude-py) < 0.08 and abs(longitude-px) < 0.08:
                bubble = {
                    "type": "bubble",
                    "hero": {
                      "type": "image",
                      "url": "https://static.vecteezy.com/system/resources/previews/000/123/653/original/free-dinner-vector-design.jpg",
                      "size": "full",
                      "aspectRatio": "20:13",
                      "aspectMode": "cover",
                      "action": {
                        "type": "uri",
                        "uri": "http://linecorp.com/"
                      }
                    },
                    "body": {
                      "type": "box",
                      "layout": "vertical",
                      "contents": [
                        {
                          "type": "text",
                          "text": name,
                          "weight": "bold",
                          "size": "xl"
                        },
                        {
                          "type": "box",
                          "layout": "vertical",
                          "margin": "lg",
                          "spacing": "sm",
                          "contents": [
                            {
                              "type": "box",
                              "layout": "baseline",
                              "spacing": "sm",
                              "contents": [
                                {
                                  "type": "text",
                                  "text": "地點",
                                  "color": "#aaaaaa",
                                  "size": "sm",
                                  "flex": 1
                                },
                                {
                                  "type": "text",
                                  "text": add,
                                  "wrap": True,
                                  "color": "#666666",
                                  "size": "sm",
                                  "flex": 5
                                }
                              ]
                            },
                            {
                              "type": "box",
                              "layout": "baseline",
                              "spacing": "sm",
                              "contents": [
                                {
                                  "type": "text",
                                  "text": "時間",
                                  "color": "#aaaaaa",
                                  "size": "sm",
                                  "flex": 1
                                },
                                {
                                  "type": "text",
                                  "text": time,
                                  "wrap": True,
                                  "color": "#666666",
                                  "size": "sm",
                                  "flex": 5
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    },
                    "footer": {
                      "type": "box",
                      "layout": "vertical",
                      "spacing": "sm",
                      "contents": [
                        {
                          "type": "box",
                          "layout": "horizontal",
                          "contents": [
                            {
                              "type": "box",
                              "layout": "horizontal",
                              "contents": [
                                {
                                  "type": "button",
                                  "action": {
                                    "type": "message",
                                    "label": "介紹",
                                    "text": dec
                                  },
                                  "style": "primary",
                                  "margin": "sm",
                                  "color": "#ea5745"
                                },
                                {
                                  "type": "button",
                                  "action": {
                                    "type": "message",
                                    "label": "預約",
                                    "text": "連絡電話:"+tel
                                  },
                                  "style": "primary",
                                  "margin": "sm",
                                  "color": "#ea5745"
                                }
                              ]
                            }
                          ],
                          "margin": "sm"
                        }
                      ],
                      "flex": 0
                    }
                  }
                bubbles.append(bubble)
        if len(bubbles) > 0 :
            bubbles = random.sample(bubbles, min(12, len(bubbles)))
            contents['contents']=bubbles
            message = FlexSendMessage(alt_text="附近店家資訊", contents=contents)
        else:
            message = TextSendMessage(text="附近未搜尋到餐廳資訊!")
        return message
#吃啥幫我選
with open('random.txt', 'r', encoding='utf-8') as file:
    options = [line.strip() for line in file.readlines()]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
@handler.add(PostbackEvent)
def handle_postback_message(event):
    if event.postback.data == "位置定位":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點選下方'位置分享'傳送目前位置，或按搜尋尋找目的地，最後按'分享'送出!", quick_reply=QuickReply(
            items=[QuickReplyButton(action=LocationAction(label="位置分享"))])))
@handler.add(MessageEvent, message=LocationMessage)
def handle_Location_message(event):
    if event.message.type == "location":
        latitude = event.message.latitude
        longitude = event.message.longitude
        message = fixed_position(latitude, longitude)
        line_bot_api.reply_message(event.reply_token, message)
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_message = event.message.text
    if user_message == "附近店家":
        FlexMessage = json.load(open('location2.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('位置定位', FlexMessage))
    elif user_message == "幫我選":
        if options:
            selected_option = random.choice(options)
            reply_message = f"抽取結果：{selected_option}"
        else:
            reply_message = "抽籤選項為空，請先匯入選項。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    elif user_message == '吃啥幫我選':
        FlexMessage = json.load(open('random.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('吃啥幫我選', FlexMessage))
    elif user_message == "外送平台":
        FlexMessage = json.load(open('fooddelivery.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('外送平台選項', FlexMessage))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)



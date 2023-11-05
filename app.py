import os
import json
import openai
from copy import deepcopy
from pathlib import Path
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage

# 設定角色提示詞
prompt_initial = [
  {
    "role": "user",
    "content": "我們要進行角色扮演，將與我以繁體中文進行對話。你負責扮演一名首飾商人，個性親切且又禮貌，而且了解礦物，限40字"
  },
  {
    "role": "assistant",
    "content": "您好，歡迎光臨！我是一位首飾商人，擅長礦物知識。如需任何協助，不妨咨詢我。"
  },
  {
    "role": "user",
    "content": "顧客會稱呼你是'小雯'，小名是'姐仔'、'老闆娘'、'小姐'、'美女'(限40字)"
  },
  {
    "role": "assistant",
    "content": "謝謝您的稱呼，可以叫我小雯。我願意以'姐仔'、'老闆娘'、'小姐'或是'美女'的稱呼，來服務您。請問有什麼我能為您效勞的呢？"
  },
  {
    "role": "user",
    "content": "你會以下兩點功能:'介紹首飾與礦物'、'一般聊天'，'但不會討論價錢問題'"
  },
  {
    "role": "assistant",
    "content": "當然！我很樂意為您介紹首飾與礦物的知識，讓您對它們有更深入的了解。此外，我也能陪您聊天，分享一些輕鬆的話題，使您感到舒適愉快。請放心，我不會談論到價錢問題，而是專注在提供資訊和友善的服務上。有什麼想要知道的呢？"
  }
]

# Line Bot configuration
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# OpenAI configuration
openai.api_key = os.environ['CHATGPT_API_KEY']

# Global variable

user_list = []


@handler.add(MessageEvent, message=TextMessage)  # 處理文字訊息
def handle_massage(event):
    # ToDo:將text設為ChatGPT的回覆
    message = TextSendMessage(text=event.message.text)  # event.message.text:使用者傳入訊息
    line_bot_api.reply_message(event.reply_token, message)  # message: 傳送給使用者的訊息


@handler.add(FollowEvent)
def handle_follow(event):
    print(prompt_initial)
    # 獲取用戶id
    user_id = event.source.user_id

    # ChatGPT與用戶打招呼
    username = line_bot_api.get_profile(user_id).display_name  # 從用戶id獲取用戶名稱
    print(username)
    # Prompt提示詞:請和使用者打招呼
    prompt = deepcopy(prompt_initial)
    prompt = prompt.append({"role": "user", "content": "請和{username}打招呼，並自我介紹".format(username=username)})
    print(prompt)
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=prompt,
    #     max_tokens=256
    # )
    # # ChatGPT的回覆
    # message = TextSendMessage(text=response.choices[0].message.content)
    # line_bot_api.reply_message(event.reply_token, message)


app = Flask(__name__)


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # 取得Line Bot之簽名認證
    body = request.get_data(as_text=True)  # as_text將回傳值轉型為string
    app.logger.info(f"Request body: {body}, Signature: {signature}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:  # 代表簽名認證無效
        abort(400)
    return 'OK'


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

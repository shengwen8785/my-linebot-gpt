import os
import json
import openai
from copy import deepcopy
from pathlib import Path
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage

# Set json(prompt) file path and load it
json_path = Path(__file__).parent / "config/prompt.json"
print(str(json_path.absolute()))
prompt_initial = json.loads(open(json_path, "r", encoding="utf-8").read())  # 角色提示

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
    # 獲取用戶id
    user_id = event.source.user_id

    # ChatGPT與用戶打招呼
    username = line_bot_api.get_profile(user_id).display_name  # 從用戶id獲取用戶名稱
    # Prompt提示詞:請和使用者打招呼
    print(json_path)
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

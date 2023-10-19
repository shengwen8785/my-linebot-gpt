import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


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


@handler.add(MessageEvent, message=TextMessage)  # 處理文字訊息
def handle_text_massage(event):
    # ToDo:將text設為ChatGPT的回覆
    message = TextSendMessage(text=event.message.text)  # event.message.text:使用者傳入訊息
    line_bot_api.reply_message(event.reply_token, message)  # message: 傳送給使用者的訊息


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
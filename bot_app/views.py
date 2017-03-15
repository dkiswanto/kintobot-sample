from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from bot_app import bots
from kinto_bot_line import settings

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
# parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

APP_NAME_INDEX = 0
COMMAND_INDEX = 1


# Webhook handler function
@csrf_exempt
def callback(request):
    if request.method == 'POST':

        body = request.body.decode('utf-8')
        signature = request.META['HTTP_X_LINE_SIGNATURE']

        try:
            # events = parser.parse(body, signature)
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden("404")

        return HttpResponse("OK")
    else:
        return HttpResponseBadRequest()


# Handle message event
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if event.source.type == "group":
        group_message(event)

    elif event.source.type == "user":
        personal_message(event)


def group_message(event):

    message_token = event.message.text.split()

    if message_token[APP_NAME_INDEX].lower() == "@kintobot":

        if len(message_token) == 1:
            bots.hello(event)

        else:
            command = message_token[COMMAND_INDEX].lower()

            if command == "hello":
                bots.hello(event)

            elif command == "help":
                bots.help_bot(event)

            elif command == "task":
                bots.task_main(event, message_token)

            elif command == "about":
                bots.about(event)

            elif command == "debug":
                bots.debug(event)

            elif command == "toxic":
                bots.toxic(event)

            else:
                message = "Command not found!!"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=message))

    else:
        # do_nothing when not mention @kintobot
        pass


def personal_message(event):
    message = "this bot only used for group purposes only, please invite it to group"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))


from __future__ import absolute_import, unicode_literals
from celery import shared_task
from linebot import LineBotApi
from linebot.models import TextSendMessage

from bot_app.models import Task
from kinto_bot_line import settings

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
FORMAT_OUTPUT = "%A, %d-%b-%Y %H:%M"


@shared_task()
def async_pre_reminder(task_id, group_id):

    # get task data
    task = Task.objects.get(pk=int(task_id))

    # reminder
    message = "[Reminder]\n\n" \
              "{}\n\n" \
              "Due Date : {}\n\n" \
              "Thank you for using @kintobot"\
        .format(task.text, task.due_date.strftime(FORMAT_OUTPUT))

    line_bot_api.push_message(group_id, TextSendMessage(text=str(message)))

    return True

@shared_task()
def async_reminder(task_id, group_id):

    # get task data
    task = Task.objects.get(pk=int(task_id))

    # final reminder
    message = "[Final Reminder]\n\n" \
              "{}\n\n" \
              "Date Assigned : {}\n\n" \
              "Thank you for using @kintobot"\
        .format(task.text, task.due_date.strftime(FORMAT_OUTPUT))

    line_bot_api.push_message(group_id, TextSendMessage(text=str(message)))

    # delete data task
    task.delete()

    return True

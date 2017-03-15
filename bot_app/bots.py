import datetime
import random

from linebot import LineBotApi
from linebot.models import TextSendMessage

from bot_app import messages
from bot_app.models import Task, Result
from kinto_bot_line import settings
from bot_app.tasks import *

from kinto_bot_line.celery import app


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
FORMAT = "%d-%m-%Y %H:%M"
FORMAT_OUTPUT = "%A, %d-%b-%Y %H:%M"
SAMPLE_DATE = "25-12-2016 19:54"


def hello(event):
    message = messages.HELLO
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))


def help_bot(event):
    message = messages.HELP
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))


def about(event):
    message = messages.ABOUT
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))


def task_main(event, message_token):
    sub_command = message_token[2].lower()

    if sub_command == "new":
        task_new(event)

    elif sub_command == "list":

        task_list(event)

    elif sub_command == "delete":
        task_delete(event, message_token)

    else:
        # wrong subcommand
        message = "wrong sub_command task"
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message))


def task_new(event):

    try:
        # Task data
        content = event.message.text.split('"')[1]
        datetime_raw = event.message.text.split('"')[2][1:]
        date = datetime.datetime.strptime(datetime_raw, FORMAT)

        # date is future?
        now = datetime.datetime.now()
        if now < date:

            group_id = event.source.group_id

            # Time Input Condition, For Async Reminder
            delta = date - now
            hour_diff = float(delta.seconds) / 3600

            # Save task
            task = Task(text=content, due_date=date, group_id=group_id)
            task.save()
            message = "Task Successfully Created\n\n" \
                      "Task : {}\n" \
                      "Date Assigned : {}"\
                .format(content, date.strftime(FORMAT_OUTPUT))

            eta = date - datetime.timedelta(hours=7)
            # Minus 1 Jam
            if delta.days == 0 and hour_diff <= 1:
                reminder_msg = "Reminder List\n" \
                               "1. Date Assigned"

                # Revoke only on Date Assigned below condition

            # Hari yang sama dan Lebih dari 1 Jam
            elif delta.days == 0 and hour_diff > 1:
                reminder_msg = "Reminder List\n" \
                               "1. -1 Jam Sebelum\n" \
                               "2. Date Assigned"

                result = async_pre_reminder.apply_async((task.id, group_id), eta=(eta - datetime.timedelta(hours=1)))
                revoke_id = result.id
                result = Result(task=task, revoke_id=revoke_id)
                result.save()

            # More than 1 days
            else:
                reminder_msg = "Reminder List\n" \
                               "1. H - 24 Jam\n" \
                               "2. H - 6 Jam\n" \
                               "3. H - 1 Jam Sebelum\n" \
                               "4. Date Assigned"

                for i in (24, 6, 1):
                    result = async_pre_reminder.apply_async((task.id, group_id), eta=(eta - datetime.timedelta(hours=i)))
                    revoke_id = result.id
                    result = Result(task=task, revoke_id=revoke_id)
                    result.save()

            # Date Assigned Reminder
            result = async_reminder.apply_async((task.id, group_id), eta=eta)
            revoke_id = result.id
            result = Result(task=task, revoke_id=revoke_id)
            result.save()

        else:
            message = "your input date is past"


    except:
        message = "ERROR FORMAT INPUT, please look at @kintobot help"

    send_message = [TextSendMessage(text=message)]
    try:
        send_message.append(TextSendMessage(text=reminder_msg))
    except NameError:
        pass

    line_bot_api.reply_message(
        event.reply_token, send_message
    )


def task_list(event):

    # get all task with current group_id
    tasks = Task.objects.filter(group_id__exact=event.source.group_id)
    message = "List Task Registered : \n\n"
    if len(tasks) != 0:
        for i, task in enumerate(tasks):
            message += "{}). ID: {}\n" \
                       "Task : {}\n" \
                       "Date : {}\n\n".\
                format(i+1, task.id, task.text, task.due_date.strftime(FORMAT_OUTPUT))
    else:
        message = "No task registered"

    line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message))


def task_delete(event, message_token):
    try:
        id_delete = message_token[3].lower()

        if id_delete == "all":

            # Delete all task based on group id
            tasks = Task.objects.filter(group_id=event.source.group_id)
            for task in tasks:

                # Cancel ALL Async Task Reminder
                for result in task.result_set.all():
                    try:
                        app.control.revoke(result.revoke_id)
                    except:
                        pass

                task.delete()

            message = "All task has been deleted"

        else:
            task = Task.objects.get(pk=int(id_delete))
            if task.group_id == event.source.group_id:

                # Cancel ALL Async Task Reminder
                for result in task.result_set.all():

                    try:
                        app.control.revoke(result.revoke_id)
                    except:
                        pass

                # Delete Task
                task.delete()
                message = "ID Task: " + id_delete + " has been successfully deleted"
            else:
                message = "wrong id task!"

    except:
        message = "wrong id task!!"

    line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message))


def toxic(event):

    option = random.randint(0, len(messages.TOXIC) - 1)
    message = messages.TOXIC[option]

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))


def debug(event):

    sub_command = event.message.text.split()[2].lower()

    if sub_command == "date":
        message = "datetime.datetime.now() - " + datetime.datetime.now().__str__()
        message = message + "\ndatetime.datetime.utcnow()" + datetime.datetime.utcnow().__str__()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif sub_command == "group_id":
        group_id = event.source.group_id
        message = "group id : " + group_id
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif sub_command == "user_id":
        user_id = event.source.user_id
        message = "user id : " + user_id
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif sub_command == "push":
        message = "push message api"
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text=message))

    else:
        message = "SUB COMMAND PLEASE!!"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


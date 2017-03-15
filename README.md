# kinto-bot

## Forked from
https://github.com/Lee-W/line_echobot [Lee-W](https://github.com/Lee-W)

## How to Deploy
* in kinto_bot_line.settings.py, edit some configuration

```
SECRET_KEY = "YOURKEY"
LINE_CHANNEL_ACCESS_TOKEN = "YOUR_TOKEN"
LINE_CHANNEL_SECRET = "YOUR_SECRET_KEY"
& Some Django Config (DEBUG, DB, ETC)
```

* Deploy to Cloud Service (Heroku / VPS)
* Set Webhook URL Callback in Line Manager

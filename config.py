import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

class TwitterConfig(object):
    CONSUMER_KEY = 'eHcU05mx45dXC0l3gOLUTAXyg'
    CONSUMER_SECRET = 'YVdIkqzw91L6dU5hEwcQkyQdcPyThb8gIOlyOdWiYNrMlGSvwJ'
    ACCESS_TOKEN = '3311641620-NlexlsblK99LbXUA51quO5Tvsq7CQA7KEUkYB3c'
    ACCESS_TOKEN_SECRET = '4UqeUPc02BLaS00sXstFJLlo8dfmxIPlCX5Kr9syTAKLa'


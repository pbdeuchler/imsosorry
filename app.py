import os
import math
import random

from flask import Flask
from slackeventsapi import SlackEventAdapter
from slack import WebClient

SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
BOT_ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
BOT_SLACK_ID = os.environ.get('BOT_SLACK_ID')

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/events', app)
slack_web_client = WebClient(BOT_ACCESS_TOKEN)

@slack_events_adapter.on("app_mention")
def handle_event(post_data):
    event_data = post_data.get('event', False)
    if event_data:
        channel = event_data.get('channel', '')
        thread_ts = event_data.get('thread_ts', event_data.get('ts', ''))
        user = event_data.get('user', '')
        if event_data.get('thread_ts', False) or (event_data.get('text', '<@' + BOT_SLACK_ID + '>') != '<@' + BOT_SLACK_ID + '>'):
            parent_ts = float(thread_ts)
            response = slack_web_client.conversations_history(
                    channel=channel,
                    oldest=int(parent_ts),
                    latest=int(math.ceil(parent_ts)),
            )
            if not response.get('ok', False):
                return ('', 503)
            messages = response.get('messages', [])
            for message in messages:
                if message.get('ts', '0.0') == thread_ts:
                    original_text = message.get('text', 'uwu :3')
                    response = slack_web_client.chat_postMessage(
                            channel=channel,
                            thread_ts=thread_ts,
                            text=uwu(original_text).replace(BOT_SLACK_ID, user.upper()),
                    )
                    if response.get('ok', False):
                        return ('', 204)
        else:
            response = slack_web_client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text="what's this? :3",
            )
            if response.get('ok', False):
                return ('', 204)

    return ('', 503)

def uwu(original_text):
    kaomoji_joy        = [' (* ^ ω ^)', ' (o^▽^o)', ' (≧◡≦)', ' ☆⌒ヽ(*\'､^*)chu', ' ( ˘⌣˘)♡(˘⌣˘ )', ' xD']
    kaomoji_embarassed = [' (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)..', ' (*^.^*)..,', '..,', ',,,', '... ', '.. ', ' mmm..', ' O.o']
    kaomoji_confuse    = [' (o_O)?', ' (°ロ°) !?', ' (ーー;)?', ' owo?']
    kaomoji_sparkles   = [' *:･ﾟ✧*:･ﾟ✧ ', ' ･ﾟﾟ･｡ ', ' ♥♡♥ ', ' uguu.., ', ' -.-']

    end_triggers = {'.': (kaomoji_joy, 2), '?': (kaomoji_embarassed, 1), '!': (kaomoji_joy, 1), ',': (kaomoji_confuse, 2)}

    result = ''

    for token in original_text.split(' '):
        if '<@' in token:
            result += token
            continue
        token = token.lower()
        last_char = token[-1:]
        end = ''
        word = ''
        if end_triggers.get(last_char, False):
            trigger = end_triggers.get(last_char)
            if random.randint(0, trigger[1]) is 0:
                end = trigger[0][random.randint(0, len(trigger[0])-1)]
        # else:
        #     if random.randint(0, 3) is 0:
        #         end = kaomoji_sparkles[random.randint(0, len(kaomoji_sparkles)-1)]

        if 'l' in token:
            if (token[-2:] == 'le') or (token[-2:] == 'll'):
                word += token[:2] + token[2:-2].replace('l', 'w').replace('r', 'w') + token[-2:] + ' '
            elif (token[-3:] == 'les') or (token[-3:] == 'lls'):
                word += token[:3] + token[3:-3].replace('l', 'w').replace('r', 'w') + token[-3:] + ' '
            else:
                word = token.replace('l', 'w').replace('r', 'w') + end + ' '
        elif 'r' in token:
            if (token[-2:] == 'er') or (token[-2:] == 're'):
                word += token[:2] + token[2:-2].replace('r', 'w') + token[-2:] + ' '
            elif (token[-3:] == 'ers') or (token[-3:] == 'res'):
                word += token[:3] + token[3:-3].replace('r', 'w') + token[-3:] + ' '
            else:
                word = token.replace('r', 'w') + end + ' '
        else:
            word = token + end + ' '

        replacements = [
            ('you\'re', 'ur'),
            ('youre', 'ur'),
            ('your', 'ur'),
            ('fuck', 'fwick'),
            ('bitch', 'meanie'),
        ]

        for replacement in replacements:
            word = word.replace(replacement[0], replacement[1])

        if (len(word) > 2) and (word.strip().isalpha()):
            if (random.randint(0, 3) is 0):
                word = word[0] + '-' + word
        result += word

    return result

# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=8000)

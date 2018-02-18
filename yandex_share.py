from flask import Flask, request
import requests
from page_parser import PageParser

from settings import APP_TOKEN, WEB_API_TOKEN

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    return 'Hello There!'


def handle_url_verification(data):
    return data.get('challenge')

def handle_link_shared(event):
    unfurls = {}
    for link in event.get('links'):
        url = link.get('url')
        origin = requests.get(url)
        p = PageParser()
        p.feed(origin.text)
        p.close()

        if p.content_type == PageParser.IMAGE:
            unfurls[url] = {
                'text': 'image',
                'image_url': p.content
            }
    response = requests.post('https://slack.com/api/chat.unfurl',
                             json={
                                 'token': WEB_API_TOKEN,
                                 'channel': event.get('channel'),
                                 'ts': event.get('message_ts'),
                                 'unfurls': unfurls
                             },
                             headers={
                                 'Content-type': 'application/json;charset=utf-8',
                                 'Authorization': 'Bearer %s' % WEB_API_TOKEN
                             })

    print('unfurl %s' % response.text)
    return('Done')


@app.route('/event-endpoint', methods=['POST'])
def event_endpoint():
    payload = request.get_json()
    p_type = payload.get('type', None)

    # Special bot verification event
    if p_type == 'url_verification':
        return handle_url_verification(payload)

    # We handle only one type of message
    if p_type != 'event_callback':
        return None

    # reject message with wrong token
    if payload.get('token') != APP_TOKEN:
        return None

    event = payload.get('event', None)
    if not event:
        return None
    event_type = event.get('type', None)

    if event_type == 'link_shared':
        return handle_link_shared(event)

    return None


if __name__ == '__main__':
        app.run(debug=True)


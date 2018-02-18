from flask import Flask, request
import requests
from html.parser import HTMLParser

from settings import APP_TOKEN, WEB_API_TOKEN

app = Flask(__name__)

class FindImage(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = None

    def handle_starttag(self, tag, attributes):
        if tag != 'img':
            return
        flag = False
        url = None
        for i in attributes:
            if i[0] == 'class':
                if 'js-view-original-resource' in i[1]:
                    flag = True
            if i[0] == 'src':
                url = i[1]
        if flag:
            self.data = url


@app.route("/", methods=['GET', 'POST'])
def hello():
    return "Hello There!"

@app.route("/event-endpoint", methods=['GET', 'POST'])
def event_endpoint():
    payload = request.get_json()
    p_type = payload.get('type', None)
    auth_valid = payload.get('token') == APP_TOKEN
    if p_type == 'url_verification':
        return payload.get('challenge')
    elif p_type == 'event_callback':
        if not auth_valid:
            return 'Go out!'
        event = payload.get('event', None)
        e_type = event.get('type', None)
        if e_type == 'link_shared':
            url = event.get('links')[0].get('url')
            origin = requests.get(url)
            p = FindImage()
            p.feed(origin.text)
            p.close()
            img = p.data
            body = {
                'token': WEB_API_TOKEN,
                'channel': event.get('channel'),
                'ts': event.get('message_ts'),
                'unfurls': {
                    url: {
                        'title': 'Test Bot',
                        'text': 'image found',
                        'image_url': 'https:%s' % img
                    }
                }
            }
            r = requests.post('https://slack.com/api/chat.unfurl',
                              json=body,
                              headers={
                                  'Content-type': 'application/json;charset=utf-8',
                                  'Authorization': 'Bearer %s' % WEB_API_TOKEN
                              })
            print('unfurl %s' % r.text)
            return('Done')

    print(payload)
    return ('Knock knock')

if __name__ == '__main__':
        app.run(debug=True)


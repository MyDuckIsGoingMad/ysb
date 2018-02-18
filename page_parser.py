from html.parser import HTMLParser

class PageParser(HTMLParser):
    UNKNOWN = 0
    IMAGE = 1
    VIDEO = 2
    DOCUMENT = 3

    def __init__(self):
        HTMLParser.__init__(self)
        self.content = None
        self.content_type = self.UNKNOWN

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
            self.content = 'https:%s' % url
            self.content_type = self.IMAGE



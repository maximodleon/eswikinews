from json import JSONEncoder
from models.article import Article
from collections import defaultdict
class ArticleJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Article):
            dict = defaultdict()
            if o.title:
                dict['title'] = o.title.encode('utf8')
            if o.content:
                dict['content'] = o.content.encode('utf8')

            cats = []
            for c in o.categories:
                if c.strip():
                    cats.append(c.strip().encode('utf8'))
            dict['categories'] = cats

        return dict
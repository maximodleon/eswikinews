# coding: utf-8

class Article:
    """
     Clase para representar un articulo
    """
    def __init__(self, title='', content='', categories=[]):
        self.title = title
        self.content = content
        self.categories = categories

    def __str__(self):
        #cats = ' {' + ','.join(self.categories) + '}'
        return self.title.encode('utf8') + "\n" + self.content.encode('utf8')# + cats
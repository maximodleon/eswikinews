# coding: utf-8

import re
import logging
import json
import codecs
from utils.jsonencoder import ArticleJSONEncoder
import xml.etree.ElementTree as ET
from models.article import Article

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Parser:
    """
     Clase para quitar los elementos innecesarios de los articulos
    """

    def __init__(self, file):
        self. archivo_regex = re.compile("\\[\\[Archivo\\:([A-Za-z0-9-_\s])+\\.(jpeg|jpg|png|PNG|JPG|JPEG)?" \
                        "(\\||\w+)+([\w+\s+]|[-_.,':]|[\\)\\(])+(\n)?", flags=re.UNICODE)
        self.foto_regex = re.compile("([\\']{2}[(]?)Foto:\s?([\w+\s+.,/-_])+([)]?([\\']{2}\\)?)(\\]{2})?)"
                                     , flags=re.UNICODE)
        self.byline_regex = re.compile('\\{\\{byline\\|.*\\}\\}', flags=re.UNICODE)
        #self.link_one_regex = re.compile('\\[\\[(:)?\\w(:es|:en)?:(\w+\s|[A-Za-z0-9-_])+\\|', flags=re.UNICODE)
        self.link_regex = re.compile("\\[\\[(:)?\\w(:es|:en)?:([A-Za-z0-9-_,.')(\s\w])+\\|", flags=re.UNICODE)
        self.link_two_regex = re.compile("\\[\\[(:)?\\w(:es|:en)?:", flags=re.UNICODE)
        self.link_categoria_regex = re.compile("\\[\\[(:)?\\w(:es)?(:\w+):([A-Za-z0-9-_,.')(\s\w])+\\|",
                                               flags=re.UNICODE)
        self.url_regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                               , flags=re.UNICODE)
        self.fecha_regex = re.compile('\\{\\{fecha\|(\w+|\s+)+\\}\\}', flags=re.UNICODE)
        self.bracketed_word_regex = re.compile('([*\s])?({){2}([\w+\s+.,-_\\|=()])+(}){2}', flags=re.UNICODE)
        self.category_regex = re.compile("(\\[){2}(:)?((Catego)(\w+))(\\:)?(\w+|\s+)+", flags=re.UNICODE)

        self.category_finder_regex = re.compile("(\\[){2}(:)?((Catego)(\w+))(\\:)?([A-Za-z0-9\s\w]+)+"
                                                , flags=re.UNICODE)

        self.other_language_regex = re.compile("(\[){2}(:)?(pt|de|en|sv)(:)([\w+\s+,.-_\\|])+((\\]){2})?"
                                               , flags=re.UNICODE)
        self.table_regex = re.compile('\\{\\|(border=[0-9])\s+(cellspacing=[0-9])[\w+\s+.,-_!|\n]+\\}'
                                      , flags=re.UNICODE)
        self.ver_fuente_regex = re.compile("([=]){4}([\s])?(Ver|Fuente)\s?([=]){4}", flags=re.UNICODE)

        self.titles_to_exclude = ['MediaWiki', 'Wikinoticias', 'Plantilla', 'Categoría'.decode("utf-8")
            , 'Ayuda', 'Broken']
        self.tag_prefix = '{http://www.mediawiki.org/xml/export-0.10/}'
        self.page_tag = 'page'
        self.title_tag = 'title'
        self.text_tag = 'text'
        self.revision_tag = 'revision'
        self.file = file

    def parse_archivo(self, text):
        if text:
            return re.sub(self.archivo_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_foto(self, text):
        if text:
            return re.sub(self.foto_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_by_line(self, text):
        if text:
            return re.sub(self.byline_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_link(self, text):
        if text:
            parsed_text = re.sub(self.link_regex, '', text.encode('utf-8').decode('utf-8'))
            parsed_text = re.sub(self.link_two_regex, '', parsed_text.encode('utf-8').decode('utf-8'))
            return re.sub(self.link_categoria_regex, '', parsed_text.encode('utf-8').decode('utf-8'))

    def parse_url(self, text):
        if text:
            return re.sub(self.url_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_fecha(self, text):
        if text:
            return re.sub(self.fecha_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_bracketed_word(self, text):
        if text:
            return re.sub(self.bracketed_word_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_other_language(self, text):
        if text:
            return re.sub(self.other_language_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_table_regex(self, text):
        if text:
            return re.sub(self.table_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_ver_fuente(self, text):
        if text:
            return re.sub(self.ver_fuente_regex, '', text.encode('utf-8').decode('utf-8'))

    def parse_category(self, text):
        if text:
            return re.sub(self.category_regex, '', text.encode('utf-8').decode('utf-8'))

    def remove_extra_text(self, text):
        """
        Remueve texto extra que aparece al final de los articulos
        :param text: texto con los del articulo que se necesita limpiar
        :return: texto sin las secciones extras
        """
        if text:
            parsed_text = text
            if parsed_text.find('== Referencias ==') > 0:
                parsed_text = parsed_text[:parsed_text.find('== Referencias ==\n')]
            if parsed_text.find('== Fuentes ==') > 0:
                parsed_text = parsed_text[:parsed_text.find('== Fuentes ==\n')]
            if parsed_text.find('== Fuente ==') > 0:
                parsed_text = parsed_text[:parsed_text.find('== Fuente ==\n')]
            if parsed_text.find('== Ver también =='.decode('utf-8')) > 0:
                parsed_text = parsed_text[:parsed_text.find('== Ver también ==\n'.decode('utf-8'))]
            if parsed_text.find("== Noticia relacionada ==".decode("utf-8")) > 0:
                parsed_text = parsed_text[:parsed_text.find("== Noticia relacionada ==".decode('utf-8'))]
            if parsed_text.find("== Artículos relacionados ==".decode("utf-8")) > 0:
                parsed_text = parsed_text[:parsed_text.find("== Artículos relacionados ==".decode('utf-8'))]
            if parsed_text.find("== Enlace externo ==".decode("utf-8")) > 0:
                parsed_text = parsed_text[:parsed_text.find("== Enlace externo ==".decode('utf-8'))]
            if parsed_text.find("== Enlaces externos ==".decode("utf-8")) > 0:
                parsed_text = parsed_text[:parsed_text.find("== Enlaces externos ==".decode('utf-8'))]
            parsed_text = parsed_text.replace('ABr)', '')
            return parsed_text

    def remove_extra_characters(self, text):
        """
         Remueve caracteres no deseados

        :param text: Texto con los caracteres no deseados
        :return:  Texto limpio, sin caracteres
        """
        if text:
            parsed_text = text
            parsed_text = parsed_text.replace("[", "")
            parsed_text = parsed_text.replace("]", "")
            parsed_text = parsed_text.replace("{", "")
            parsed_text = parsed_text.replace("}", "")
            parsed_text = parsed_text.replace("|", " ")
            parsed_text = parsed_text.replace("-", "")
            parsed_text = parsed_text.replace("&nbsp;", "")
            parsed_text = parsed_text.replace(":'", "")
            parsed_text = parsed_text.replace("'", "")
            parsed_text = parsed_text.replace("#", "")
            parsed_text = parsed_text.replace("':", "")
            parsed_text = parsed_text.replace("=", "")
            parsed_text = parsed_text.replace("*", "")
            parsed_text = parsed_text.replace("/", "")
            parsed_text = parsed_text.replace("<--", "")
            parsed_text = parsed_text.replace("-->", "")
            parsed_text = parsed_text.replace("<!--", "")
            parsed_text = parsed_text.replace(">", "")
            parsed_text = parsed_text.replace("<", "")

            parsed_text = parsed_text.replace('__NOTOC__', '')

            return parsed_text

    def is_news_article(self, page):
        """
         Determina si es un aticulo o es metadata

        :param page: Tag que contiene el titulo a validar
        :return: True or False
        """
        title = page.find(self.tag_prefix + self.title_tag).text
        for meta in self.titles_to_exclude:
            if title.startswith(meta):
                logging.info("{} No es un articulo. Se ignora".format(title.encode('utf8')))
                return False
        logging.info("{} Es un articulo. Se procesa".format(title.encode('utf8')))
        return True

    def process_page_tag(self, root):
        """
        Procesa los tags a partir del tag raiz que se le pase
        :param root: Raiz por donde empezar a leer
        :return:
        """
        pages = root.findall(self.tag_prefix + self.page_tag)
        articles = []
        for page in pages:
            if self.is_news_article(page):
                article = self.parse_text(page)
                if article:
                    articles.append(article)
        return articles

    def parse_text(self, page):
        """
         Metodo para limpiar el texto
        :param page: Tag que contiene el texto a limpiar
        :return:  texto limpio
        """
        text = page.find(self.tag_prefix + self.revision_tag).find(self.tag_prefix + self.text_tag).text
        title = page.find(self.tag_prefix + self.title_tag).text
        categories = []
        #
        text = self.parse_archivo(text)
        text = self.parse_foto(text)
        text = self.parse_by_line(text)
        text = self.parse_link(text)
        text = self.parse_url(text)
        text = self.parse_fecha(text)
        text = self.parse_bracketed_word(text)
        #
        if text:
            categories = re.findall(self.category_finder_regex, text)
        #
        text = self.parse_category(text)
        text = self.parse_other_language(text)
        text = self.parse_table_regex(text)
        text = self.parse_ver_fuente(text)
        text = self.remove_extra_text(text)
        text = self.remove_extra_characters(text)

        categorias = []
        for cat in categories:
            categorias.append(cat[6])

        if text:
            if 'REDIRECT' in text or 'redirect' in text:
                return None

        return Article(title=title, content=text, categories=categorias)

    def parse_file(self):
        logging.info("Leyendo archivo {}".format(self.file))
        tree = ET.parse(self.file)
        root = tree.getroot()
        articles = self.process_page_tag(root)
        f = codecs.open("output/data.json", 'w', "utf8")
        f.write(json.dumps(articles, cls=ArticleJSONEncoder, ensure_ascii=False, encoding='utf8'))
        f.close()

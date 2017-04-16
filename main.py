# coding: utf-8
import xml.etree.ElementTree as ET
import re

tag_prefix = '{http://www.mediawiki.org/xml/export-0.10/}'
page_tag = 'page'
title_tag = 'title'
text_tag = 'text'
revision_tag = 'revision'
titles_to_exclude =['MediaWiki', 'Wikinoticias', 'Plantilla','Categoría'.decode("utf-8"), 'Ayuda','Broken']

archivo_regex = "\\[\\[Archivo\\:([A-Za-z0-9-_\s])+\\.(jpeg|jpg|png|PNG|JPG|JPEG)?" \
                "(\\||\w+)+([\w+\s+]|[-_.,':]|[\\)\\(])+(\n)?"
foto_regex = "([\\']{2}[(]?)Foto:\s?([\w+\s+.,/-_])+([)]?([\\']{2}\\)?)(\\]{2})?)"
byline_regex = '\\{\\{byline\\|.*\\}\\}'
link_start_regex = '\\[\\[(:)?\\w(:es)?\\:'
link_end_regex = "\\|([\w+\s+.,-_'])+(\\]){2}"
url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
fecha_regex = '\\{\\{fecha\|(\w+|\s+)+\\}\\}'
bracketed_word_regex = '([*\s])?({){2}([\w+\s+.,-_\\|=()])+(}){2}'
category_regex = "(\\[){2}(:)?((Catego)(\w+))(\\:)?(\w+|\s+)+"
other_language_regex = "(\[){2}(:)?(pt|de|en|sv)(:)([\w+\s+,.-_\\|])+((\\]){2})?"
table_regex = '\\{\\|(border=[0-9])\s+(cellspacing=[0-9])[\w+\s+.,-_!|\n]+\\}'
ver_fuente_regex = "([=]){4}([\s])?(Ver|Fuente)\s?([=]){4}"

def is_news_article(title):
    for meta in titles_to_exclude:
        if title.startswith(meta):
            return False
    return True


def parse_text(text):
    if (text.find("#REDIRECT")) >= 0:
        return ''

    parsed_text = text.encode('utf-8').decode('utf-8')
    parsed_text = re.sub(archivo_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(foto_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(byline_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(link_start_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(link_end_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(url_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(fecha_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(bracketed_word_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(category_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(other_language_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(table_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)
    parsed_text = re.sub(ver_fuente_regex, '', parsed_text.encode('utf-8').decode('utf-8'), flags=re.UNICODE)

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
    print parsed_text#.strip("\n")#.rstrip("\n")


def process_page_tag(root):
    pages = root.findall(tag_prefix + page_tag)
    count = 0
    for page in pages:
        if is_news_article(page.find(tag_prefix + title_tag).text):
            count = count + 1
            parse_text(page.find(tag_prefix + revision_tag).find(tag_prefix + text_tag).text)
            if count == 80:
                break


def main():
    tree = ET.parse('eswikinews-20170401-pages-articles.xml')
    root = tree.getroot()
    process_page_tag(root)

if __name__ == "__main__":
    main()

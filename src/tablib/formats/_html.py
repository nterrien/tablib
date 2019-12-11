""" Tablib - HTML export support.
"""

import codecs
from io import BytesIO

from MarkupPy import markup
import requests
import lxml.html as lh


class HTMLFormat:
    BOOK_ENDINGS = 'h3'

    title = 'html'
    extensions = ('html', )

    @classmethod
    def export_set(cls, dataset):
        """HTML representation of a Dataset."""

        stream = BytesIO()

        page = markup.page()
        page.table.open()

        if dataset.headers is not None:
            new_header = [item if item is not None else '' for item in dataset.headers]

            page.thead.open()
            headers = markup.oneliner.th(new_header)
            page.tr(headers)
            page.thead.close()

        for row in dataset:
            new_row = [item if item is not None else '' for item in row]

            html_row = markup.oneliner.td(new_row)
            page.tr(html_row)

        page.table.close()

        # Allow unicode characters in output
        wrapper = codecs.getwriter("utf8")(stream)
        wrapper.writelines(str(page))

        return stream.getvalue().decode('utf-8')

    @classmethod
    def export_book(cls, databook):
        """HTML representation of a Databook."""

        stream = BytesIO()

        # Allow unicode characters in output
        wrapper = codecs.getwriter("utf8")(stream)

        for i, dset in enumerate(databook._datasets):
            title = (dset.title if dset.title else 'Set %s' % (i))
            wrapper.write('<{}>{}</{}>\n'.format(cls.BOOK_ENDINGS, title, cls.BOOK_ENDINGS))
            wrapper.write(dset.html)
            wrapper.write('\n')

        return stream.getvalue().decode('utf-8')

    @classmethod
    def import_set (cls, dset, in_stream, id=None):
        """Returns dataset from HTML stream."""

        dset.wipe()

        page = requests.get(in_stream)
        doc = lh.fromstring(page.content)
        tables = doc.cssselect("table")

        # Si précisé, on récupère la bonne table, sinon en prend la première
        ##TODO
        table = tables[0]

        tr_elements = table.xpath('//tr')

        # On regarde si la première ligne est un Header ou pas si oui -> dataset.header; sinon -> pas de header
        ##TODO

        for tr in tr_elements:
            dset.append([t.text_content() for t in tr])

        return dset

    @classmethod
    def detect(cls, stream):
        # returns True if given stream is parsable as xxx
        try:
            requests.get(stream)
            return True
        except Exception:
            return False


# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree

from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint

#from collective.nitf.content import genre_default_value
#from collective.nitf.content import section_default_value
#from collective.nitf.content import urgency_default_value


def get_text(dom, subelemet, attribute=None):
    """ Return the text value for a node xor a attribute value from that node.
    """
    elem = dom.find(subelemet)
    if elem is not None:
        if attribute is None:
            return elem.text

        elif attribute in elem.keys():
            return elem.get(attribute)

    return ''


def get_date_path(dom, subelemet, attribute):
    """ Return a path ibased on a date value normalized into ISO8601
        Note: Only work with the basic format.
    """
    text =  get_text(dom, subelemet, attribute)
    # We only need the YYYYMMDD part from the string
    date = 


class XMLSource(object):
    """ Process an string containing a xml representation of a nitf object.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for data in self.previous:
            images = []
            videos = []
            item = {'id': '',
                    'path': '',
                    'title': '',
                    'subtitle': '',
                    'description': '',
                    'byline': '',
                    'text': '',
                    'genre': '',
                    'section': '',
                    'urgency': '',
                    'location': ''}

            dom = etree.fromstring(data)
            head = dom.find('head')
            body = dom.find('body')

            item['id'] = get_text(head, 'docdata/doc-id', 'id-string').lower()
            item['path'] = get_date_path(head, 'docdata/date.release', 'norm')
            item['title'] = get_text(head, 'title')
            item['genre'] = get_text(head, 'tobject/tobject.property',
                                           'tobject.property.type')
            item['section'] = get_text(head, 'pubdata', 'position.section')
            item['urgency'] = get_text(head, 'docdata/urgency', 'ed-urg')
            item['location'] = ", ".join([
                get_text(head, 'docdata/evloc', 'city'),
                get_text(head, 'docdata/evloc', 'state-prov'),
                get_text(head, 'docdata/evloc', 'iso-cc')])

            item['subtitle'] = get_text(body, 'body.head/hedline/hl2')
            item['description'] = get_text(body, 'body.head/abstract')
            item['byline'] = get_text(body, 'body.head/byline/person')

            for elem in list(body.find('body.content')):
                if elem.tag == 'media':
                    image = dict(elem.find('media-reference'))
                    image['alt'] = get_text(elem, 'media-caption')
                    images.append(image)

                elif elem.tag == 'video':
                    video = dict(elem.find('media-reference'))
                    video['alt'] = get_text(elem, 'media-caption')
                    videos.append(video)

                else:   # other tag are considered part of the body text and
                        # should be preserved.
                    item['text'] += etree.tostring(elem)

            yield item

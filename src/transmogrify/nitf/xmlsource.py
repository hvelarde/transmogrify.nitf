# -*- coding: utf-8 -*-
from isodate import parse_datetime
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


class XMLSource(object):
    """ Process an string containing a xml representation of a nitf object.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for data in self.previous:
            item = {'_path': None,
                    '_type': 'collective.nitf.content',
                    # plone.app.dexterity.behaviours.metadata.IBasic
                    'title': None, 'description': None,
                    # plone.app.dexterity.behaviours.metadata.ICategorization
                    'subject': [], 'language': '',
                    # plone.app.dexterity.behaviours.metadata.IPublication
                    'effective': None, 'expires': None,
                    # plone.app.dexterity.behaviours.metadata.IOwnership
                    'creators': [], 'contributors': [], 'rights': None,
                    # TODO: How the standar manage refenreces and related items.
                    # plone.app.referenceablebehavior.referenceable.IReferenceable
                    #'_plone.uuid': '',
                    # plone.app.relationfield.behavior.IRelatedItems
                    # 'relatedItems': (),
                    # collective.nitf.content.INITF
                    'subtitle': '', 'byline': '', 'text': '', 'genre': '',
                    'section': '', 'urgency': '', 'location': '',
                    # objects that should be created inside of the current
                    # NITF object.
                    '_media': {'images': [],
                              'videos': []}
                    }

            dom = etree.fromstring(data)
            head = dom.find('head')
            body = dom.find('body')

            item['_path'] = get_text(head, 'docdata/doc-id', 'id-string').lower()
            item['title'] = get_text(head, 'title')
            item['subject'] = [k.get('key') for k in \
                            list(head.find('docdata/key-list')) if k.get('key')]
            #item['language']
            sdate = get_text(head, 'docdata/date.release', 'norm')
            if sdate:
                item['effective'] = parse_datetime(sdate)

            sdate = get_text(head, 'docdata/date.expire', 'norm')
            if sdate:
                item['expires'] = parse_datetime(sdate)

            #sdate = get_text(head, 'docdata/date.issue', 'norm')
            #if sdate:
            #    item['issue'] = parse_datetime(sdate)

            item['genre'] = get_text(head, 'tobject/tobject.property',
                                    'tobject.property.type')
            item['section'] = get_text(head, 'pubdata', 'position.section')
            item['urgency'] = get_text(head, 'docdata/urgency', 'ed-urg')

            item['description'] = get_text(body, 'body.head/abstract/p')
            item['location'] = get_text(body, 'body.head/dateline/location')
            item['subtitle'] = get_text(body, 'body.head/hedline/hl2')
            item['byline'] = get_text(body, 'body.head/byline/person')

            for elem in list(body.find('body.content')):
                if elem.tag == 'media' and elem.get('media-type') == 'image':
                    image = elem.find('media-reference').attrib
                    image['media-caption'] = get_text(elem, 'media-caption')
                    item['_media']['images'].append(image)

                elif elem.tag == 'media' and elem.get('media-type') == 'video':
                    video = elem.find('media-reference').attrib
                    video['media-caption'] = get_text(elem, 'media-caption')
                    item['_media']['videos'].append(video)

                else:   # other tag are considered part of the body text and
                        # should be preserved.
                    item['text'] += etree.tostring(elem)

            yield item

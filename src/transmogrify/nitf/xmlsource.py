# -*- coding: utf-8 -*-
import logging
import urlparse
import xml.etree.ElementTree as etree
from isodate import parse_datetime
from urllib2 import urlopen, URLError

from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile


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
        if 'directory' in options:
            self.directory = resolvePackageReferenceOrFile(options['directory'])
        else:
            self.directory = None

        self.logger = logging.getLogger(name)

    def __iter__(self):
        for data in self.previous:
            item = {'_path': None,
                    '_type': 'collective.nitf.content',
                    # plone.app.dexterity.behaviours.metadata.IBasic
                    'title': None, 'description': None,
                    # plone.app.dexterity.behaviours.metadata.ICategorization
                    'subjects': [], 'language': '',
                    # plone.app.dexterity.behaviours.metadata.IPublication
                    'effective': None, 'expires': None,
                    # plone.app.dexterity.behaviours.metadata.IOwnership
                    'creators': [], 'contributors': [], 'rights': None,
                    # TODO: How the standar manage refenreces and related items?.
                    # plone.app.referenceablebehavior.referenceable.IReferenceable
                    #'_plone.uuid': '',
                    # plone.app.relationfield.behavior.IRelatedItems
                    # 'relatedItems': (),
                    # collective.nitf.content.INITF
                    'subtitle': '', 'byline': '', 'text': '', 'genre': '',
                    'section': '', 'urgency': '', 'location': '',
                    }

            dom = etree.fromstring(data)
            head = dom.find('head')
            body = dom.find('body')

            item['_path'] = get_text(head, 'docdata/doc-id', 'id-string').lower()
            item['title'] = get_text(head, 'title')
            item['subjects'] = [k.get('key') for k in \
                            list(head.find('docdata/key-list')) if k.get('key')]
            #item['language']
            sdate = get_text(head, 'docdata/date.release', 'norm')
            if sdate:
                item['effective'] = parse_datetime(sdate)

            sdate = get_text(head, 'docdata/date.expire', 'norm')
            if sdate:
                item['expires'] = parse_datetime(sdate)

            # This field is not implemented in the collective.nitf
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

            # The list of media items to yield, like atimages objects and video
            # references.
            media_items = []
            for elem in list(body.find('body.content')):
                if elem.tag == 'media' and elem.get('media-type') == 'image':
                    # media-type image list of attributes:
                    # - mime-type, source, alternate-text, height, width.
                    image = {'_path': None,
                             '_type': 'Image',
                             'title': None,
                             'description': None,
                             'image': None,
                             '_data': None,
                             '_mimetype': None,
                             }

                    media = elem.find('media-reference')
                    src = media.get('source', None)
                    path = media.get('alternate-text', None)
                    image['title'] = media.get('alternate-text', None)
                    image['_mimetype'] = media.get('mime-type')
                    image['description'] = get_text(elem, 'media-caption')

                    if None in (src, path, image['_mimetype']):
                        self.logger.debug(
                            "item path: {0}, incomplete data image src: {1}"
                             .format(item['_path']), path)
                        continue

                    if self.directory is not None:
                    # Change the url schema to retrive the file from the
                    # filesystem and insert the source directory path.
                        url = urlparse.urlparse(src)
                        sdir = urlparse.urlparse(self.directory)
                        src = urlparse.urlunsplit(('file',
                                "{0}/{1}".format(sdir.path, url.netloc),
                                url.path, url.query, url.fragment))

                    try:
                        fd = urlopen(src)
                    except URLError:
                        self.logger.debug(
                            "item path: {0}, can't retrieve image from url: {1}"
                             .format(item['_path']), src)
                        continue

                    image['_data'] = fd.read()
                    fd.close()
                    image['_path'] = "{0}/{1}".format(item['_path'], path)
                    # HACK: This is to support folder archive based on the
                    # effective date (original publication date).
                    image['effective'] = item['effective']

                    media_items.append(image)

                elif elem.tag == 'media' and elem.get('media-type') == 'video':
                    # TODO: manage video refenrence.
                    # media-type video list of attributes:
                    # - media-type, source, alternate-text.
                    video = {}
                    # media_items.append(video)
                else:   # other tag are considered part of the body text and
                        # should be preserved.
                    item['text'] += etree.tostring(elem)

            # First we need create the nitf object
            yield item
            # Media items should be created after the nitf object.
            for media_item in media_items:
                yield media_item

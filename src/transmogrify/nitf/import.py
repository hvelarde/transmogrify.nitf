# -*- coding: utf-8 -*-

import os

from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import resolvePackageReferenceOrFile


class DirectorySource(object):
    """ Reads the directory's contents and yield a readlines for every file.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        """ Takes two options:

            directory: A full path to a directory or a relative path inside a
                       package in the form collective.example:datadir.

            suffix: The extension of files that should be processed.
        """
        self.previous = previous
        self.directory = resolvePackageReferenceOrFile(options['directory'])
        self.suffix = ".{0}".format(options['suffix'].split())

    def __iter__(self):
        for item in self.previous:
            yield item

        for filename in os.listdir(self.directory):
            if filename.endswith(self.suffix):
                filepath = os.path.join(self.directory, filename)
                with open(filepath, 'r') as item:
                    yield item.read()

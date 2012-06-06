Introduction
============


Blueprints that this package include.
========================================

 - transmogrify.nitf.import.sourcedirectory
 - transmogrify.nitf.xmlsource.xmlprocessor


transmogrify.nitf.import.sourcedirectory
========================================

This blueprint read files from an specific directory that have a determined suffix.

Options:
--------

directory:
    Reference for a directory inside the package or an absolute path.

suffix:
    Extension of the files to be read.


transmogrify.nitf.xmlsource.xmlprocessor
========================================

Process an string that contain a representation of an xml.

Options:
--------

directory:
    Reference for a directory inside the package or an absolute path. If is set
    the blueprint lookup for images, referenced in the xml, inside that
    directory.
    The idea of this is reduce the time of import avoiding download the image
    from the network. Also allows run the import in locations where the
    connectivity is restricted.
    To be capable of access to the images, is necessary to avoiding name
    collisions, create a directory structure that emulates the server name and
    path of the original url.

Example:

If the src image attribute is: ::

    http://example.net/images/picture.jpg

And the option 'directory' is '/foo/bar', then the image must be located in::

    /foo/bar/example.net/images/picture.jpg

This could be create in a easy way with the command wget, the only thing that
you need is a file with the url for all images (ex: images.list) and then run
the command as bellow: ::

    $ wget -nc -x -i images.list


Configuration examples:
=======================
::

    [sourcedirectory]
    blueprint = transmogrify.nitf.import.sourcedirectory
    directory = transmogrify.nitf:data
    suffix = xml

    [xmlprocessor]
    blueprint = transmogrify.nitf.xmlsource.xmlprocessor
    directory = transmogrify.nitf:data/images


Excecution mode:
================

This package contain two pipelines and a view that list the registered
pipelines, so you could select which of one to run.

Then go into the url::

    http://localhost:8080/Plone/@@transmogrify-nitf

And the press "Run".

# -*- coding: utf-8 -*-

from five import grok

from zope import schema
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from z3c.form import button
from z3c.form.interfaces import ActionExecutionError

from plone.directives import form

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from collective.transmogrifier.transmogrifier import Transmogrifier
from collective.transmogrifier.transmogrifier import configuration_registry

from transmogrify.nitf import _


@grok.provider(IContextSourceBinder)
def pipelines_list(context):
    items = []
    pids = configuration_registry.listConfigurationIds()
    for pid in pids:
        pipeline = configuration_registry.getConfiguration(pid)
        items.append((pipeline['title'], pipeline['id']))

    return SimpleVocabulary.fromItems(items)


class INITFTransmogrifierForm(form.Schema):
    """ From definition.
    """
    pipeline = schema.Choice(
                title = _(u'Pipelines'),
                description = _(u'Select a transmogrifier pipelie to run.'),
                source = pipelines_list,
                )


class NITFTransmogrifierForm(form.SchemaForm):
    """ Form view to select an transmogrifier pipeline registered.
    """
    grok.context(IPloneSiteRoot)
    grok.name('transmogrify-nitf')
    grok.require('cmf.ManagePortal')

    schema = INITFTransmogrifierForm
    ignoreContext = True

    label = _(u'Transmogrifiers')

    def update(self):
        """
        """
        self.request.set('disable_border', True)
        super(NITFTransmogrifierForm, self).update()

    @button.buttonAndHandler(u"Run")
    def handle_action(self, action):
        """ Processes the form and runs the selected pipeline.
        """
        data, errors = self.extractData()
        if errors:
            self.status = self.formErorrsMessage
            return

        pipeline_id = data.get('pipeline', None)
        pipelines = configuration_registry.listConfigurationIds()
        if pipeline_id is not None and pipeline_id in pipelines:
            transmogrifier = Transmogrifier(self.context)
            transmogrifier(pipeline_id)
            pipeline = configuration_registry.getConfiguration(pipeline_id)
            IStatusMessage(self.request).addStatusMessage('{0} {1}'
                .format(pipeline['title'], _('successfully executed.')), 'info')

            self.request.response.redirect(self.context.absolute_url())
        else:
            raise ActionExecutionError(Invalid('{0}: {1}'
                .format(_(u'Invalid pipeline'), pipeline_id)))


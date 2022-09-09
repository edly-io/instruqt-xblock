"""xblock embeds instruqt track in Open edX."""

import json
import logging

import pkg_resources
from django.template import Context, Template
from django.utils import translation
from webob import Response
from xblock.completable import CompletableXBlockMixin
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _

log = logging.getLogger(__name__)


@XBlock.needs("i18n")
class InstruqtXBlock(StudioEditableXBlockMixin, CompletableXBlockMixin, XBlock):
    """
    This xblock embeds instruqt track in Open edX.
    """

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Instruqt track",
        scope=Scope.settings,
    )

    track_embed_code = String(
        display_name=_("Track embed code"),
        multiline_editor=True,
        help=_("Copy track code from instruqt track details page and paste here"),
        scope=Scope.settings,
    )

    track_iframe_width = Integer(
        display_name=_("Width"),
        help=_("Width of IFRAME having instruqt track"),
        default=1140,
        scope=Scope.settings,
    )

    track_iframe_height = Integer(
        display_name=_("Height"),
        help=_("Height of IFRAME having instruqt track"),
        default=640,
        scope=Scope.settings,
    )

    editable_fields = ('display_name', 'track_embed_code', 'track_iframe_width', 'track_iframe_height')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context):
        """
        Renders template fetch from a path after injecting context
        """
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def student_view(self, context=None):  # lint-amnesty, pylint: disable=unused-argument
        """
        The primary view of the InstruqtXBlock, shown to students when viewing courses.
        """
        template = self.render_template("static/html/instruqtxblock.html", {"self": self})
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/instruqtxblock.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))

        frag.add_javascript(self.resource_string("static/js/src/instruqtxblock.js"))
        frag.initialize_js('InstruqtXBlock')
        return frag

    @XBlock.json_handler
    def completion_handler(self, data, suffix=''):  # lint-amnesty, pylint: disable=unused-argument
        """
        Handler to trigger completion event
        """
        save_completion = False
        try:
            self.emit_completion(1.0)
            save_completion = True
        except BaseException as exp:
            log.error("Error while marking completion %s", exp)

        return Response(
            json.dumps({"result": {"save_completion": save_completion}}),
            content_type="application/json",
            charset="utf8",
        )

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("InstruqtXBlock",
             """<instruqtxblock/>
             """),
            ("Multiple InstruqtXBlock",
             """<vertical_demo>
                <instruqtxblock/>
                <instruqtxblock/>
                <instruqtxblock/>
                </vertical_demo>
             """),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = 'public/js/translations/{locale_code}/text.js'
        lang_code = locale_code.split('-')[0]
        for code in (locale_code, lang_code, 'en'):
            loader = ResourceLoader(__name__)
            if pkg_resources.resource_exists(
                    loader.module_name, text_js.format(locale_code=code)):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop('Dummy')

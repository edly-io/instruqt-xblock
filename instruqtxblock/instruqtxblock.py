"""xblock embeds instruqt track in Open edX."""

import json
import logging

import pkg_resources
from django.template import Context, Template
from django.utils import translation
from web_fragments.fragment import Fragment
from webob import Response
from xblock.completable import CompletableXBlockMixin
from xblock.core import XBlock
from xblock.fields import Boolean, Integer, Scope, String
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _

log = logging.getLogger(__name__)


@XBlock.needs("i18n")
@XBlock.needs('user')
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
        default='',
        help=_("Copy track code from instruqt track details page and paste here"),
        scope=Scope.settings,
    )

    track_iframe_width = Integer(
        display_name=_("Width"),
        help=_("Width of IFRAME having instruqt track"),
        default=940,
        scope=Scope.settings,
    )

    track_iframe_height = Integer(
        display_name=_("Height"),
        help=_("Height of IFRAME having instruqt track"),
        default=640,
        scope=Scope.settings,
    )

    total_challenges = Integer(
        help=_("Number of challenges in track. Set it to 0 if track does not have any challenge"),
        default=0,
        scope=Scope.user_state,
    )

    completed_challenges = Integer(
        help=_("Number of challenges completed by user"),
        default=0,
        scope=Scope.user_state,
    )

    has_score = Boolean(
        display_name=_("Calculate score on challenge completion"),
        help=_(
            "Selecting this option means score is calculated every time a learner completes a challenge. e.g \
                if 2 out of 5 challenges are completed score would be 0.4 (2/5)"
        ),
        default=False,
        scope=Scope.settings,
    )

    editable_fields = (
        'display_name', 'track_embed_code', 'track_iframe_width',
        'track_iframe_height', 'has_score'
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _get_user_id(self):
        """
        Returns external user id for lti type when runtime is LMS or returns `student_1`\
             for other runtimes like workbench
        """
        user_service = self.runtime.service(self, 'user')
        user_id = 'student_1'
        if hasattr(user_service, 'get_external_user_id'):
            user_id = user_service.get_external_user_id('lti')

        return user_id

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
        user_id = self._get_user_id()
        track_url = '{}&icp_user_id={}'.format(self.track_embed_code, user_id)
        template = self.render_template(
            "static/html/instruqtxblock.html",
            {"self": self, "track_url": track_url}
        )
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
        Handler to trigger completion and score event
        """
        save_track_completion, save_challenge_completion = False, False

        if data['event'] == "track.completed":
            try:
                self.emit_completion(1.0)
                save_track_completion = True
            except BaseException as exp:
                log.error("Error while marking track completion %s", exp)

        if data['event'] == "track.challenge_completed":
            try:
                total_challenges = data['params']['total_challenges']
                if self.completed_challenges < total_challenges:
                    completed_challenges = self.completed_challenges + 1
                else:
                    # Reset completed_challenges if learner has already completed track
                    completed_challenges = 0

                self.completed_challenges = completed_challenges
                self.total_challenges = total_challenges
                if self.has_score and total_challenges > 0:
                    grade_dict = {
                        'value': round(completed_challenges/total_challenges, 2),
                        'max_value': 1,
                        'only_if_higher': True,
                    }
                    self.runtime.publish(self, 'grade', grade_dict)
                save_challenge_completion = True
            except BaseException as exp:
                log.error("Error while marking challenge completion %s", exp)

        return Response(
            json.dumps(
                {
                    "result":
                    {
                        "save_track_completion": save_track_completion,
                        "save_challenge_completion": save_challenge_completion,
                    }
                }
            ),
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

"""
Tests for the remaining InstruqtXBlock behaviour: user id, grading, i18n lookup and workbench helpers.
"""

import importlib
import json
from unittest.mock import Mock, patch

import pytest

from instruqtxblock.instruqtxblock import InstruqtXBlock


def post_event(block, event, **params):
    """Call completion_handler with a JSON event body and return the decoded result."""
    body = json.dumps({"event": event, "params": params}).encode()
    response = block.completion_handler(Mock(method='POST', body=body))
    assert response.status_code == 200
    return response.json["result"]


def test_get_user_id_defaults_for_workbench(block):
    """Runtimes without an external id lookup fall back to `student_1`."""
    with patch.object(block.runtime, 'service', return_value=object()):
        assert block._get_user_id() == 'student_1'


def test_get_user_id_uses_lti_external_id(block):
    """LMS-style user services provide the external LTI id."""
    user_service = Mock()
    user_service.get_external_user_id.return_value = 'ext-42'
    with patch.object(block.runtime, 'service', return_value=user_service):
        assert block._get_user_id() == 'ext-42'
    user_service.get_external_user_id.assert_called_once_with('lti')


def test_student_view_embeds_track_with_user_id(block):
    """The iframe src gets the learner id appended and the i18n script is included when available."""
    block.track_embed_code = '<iframe src="https://play.instruqt.com/embed/acme/tracks/t?token=abc"></iframe>'
    with patch.object(InstruqtXBlock, '_get_statici18n_js_url', return_value='public/js/translations/en/text.js'):
        with patch.object(block.runtime, 'local_resource_url', return_value='/resource/text.js') as local_url:
            fragment = block.student_view()
    local_url.assert_called_once_with(block, 'public/js/translations/en/text.js')
    assert '&icp_user_id=student_1' in fragment.content
    assert '/resource/text.js' in [res.data for res in fragment.resources]
    assert fragment.js_init_fn == 'InstruqtXBlock'


def test_track_completed_emit_failure_is_logged(block):
    """A failing completion publish is reported as not saved instead of raising."""
    with patch.object(block, 'emit_completion', side_effect=RuntimeError('boom')):
        with patch('instruqtxblock.instruqtxblock.log.error') as log_error:
            result = post_event(block, 'track.completed')
    assert result == {"save_track_completion": False, "save_challenge_completion": False}
    assert log_error.call_args[0][0] == 'Error while marking track completion %s'


def test_unknown_event_is_ignored(block):
    """Events other than the two handled ones change nothing."""
    result = post_event(block, 'track.started')
    assert result == {"save_track_completion": False, "save_challenge_completion": False}
    assert block.completed_challenges == 0


def test_challenge_completed_publishes_grade_when_scored(block):
    """Scored blocks publish completed/total as the grade."""
    block.has_score = True
    with patch.object(block.runtime, 'publish') as publish:
        result = post_event(block, 'track.challenge_completed', total_challenges=3)
    assert result["save_challenge_completion"] is True
    assert (block.completed_challenges, block.total_challenges) == (1, 3)
    publish.assert_called_once_with(block, 'grade', {'value': 0.33, 'max_value': 1, 'only_if_higher': True})


def test_challenge_completed_without_score_publishes_nothing(block):
    """Unscored blocks only track progress."""
    with patch.object(block.runtime, 'publish') as publish:
        result = post_event(block, 'track.challenge_completed', total_challenges=3)
    assert result["save_challenge_completion"] is True
    publish.assert_not_called()


def test_challenge_completed_with_zero_total_publishes_nothing(block):
    """A track without challenges never produces a grade, even when scoring is on."""
    block.has_score = True
    with patch.object(block.runtime, 'publish') as publish:
        post_event(block, 'track.challenge_completed', total_challenges=0)
    publish.assert_not_called()


def test_challenge_counter_resets_after_track_is_finished(block):
    """Completing more challenges than the track has restarts the counter."""
    block.completed_challenges = 3
    post_event(block, 'track.challenge_completed', total_challenges=3)
    assert block.completed_challenges == 0


def test_workbench_scenarios_are_xml_snippets():
    """Both canned scenarios reference the block's tag."""
    scenarios = InstruqtXBlock.workbench_scenarios()
    assert [title for title, _ in scenarios] == ["InstruqtXBlock", "Multiple InstruqtXBlock"]
    assert all('<instruqtxblock/>' in xml for _, xml in scenarios)


def test_get_dummy_returns_marker_string():
    """The dummy method only exists so i18n extraction has a string to find."""
    assert InstruqtXBlock.get_dummy() == 'Dummy'


def test_statici18n_url_none_without_active_language():
    """No active language means no translation bundle."""
    with patch('instruqtxblock.instruqtxblock.translation.get_language', return_value=None):
        assert InstruqtXBlock._get_statici18n_js_url() is None


@pytest.mark.parametrize('available, expected', [
    ({'fr-ca'}, 'public/js/translations/fr-ca/text.js'),
    ({'fr'}, 'public/js/translations/fr/text.js'),
    ({'en'}, 'public/js/translations/en/text.js'),
    (set(), None),
])
def test_statici18n_url_falls_back_from_locale_to_language_to_english(available, expected):
    """The most specific existing translation bundle wins."""
    def exists(_module, path):
        return path.split('/')[3] in available

    with patch('instruqtxblock.instruqtxblock.translation.get_language', return_value='fr-ca'):
        with patch('instruqtxblock.instruqtxblock.pkg_resources.resource_exists', side_effect=exists):
            assert InstruqtXBlock._get_statici18n_js_url() == expected


def test_locale_settings_read_secret_from_environment(monkeypatch):
    """The i18n tooling settings module takes its secret from DJANGO_SECRET."""
    from instruqtxblock.locale import settings as locale_settings

    monkeypatch.setenv('DJANGO_SECRET', 'from-env')
    assert importlib.reload(locale_settings).SECRET_KEY == 'from-env'
    monkeypatch.delenv('DJANGO_SECRET')
    assert importlib.reload(locale_settings).SECRET_KEY == 'open_secret'

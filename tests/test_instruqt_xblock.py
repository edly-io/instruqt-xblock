"""
Tests for the Instruqt XBlock
"""

import json
import unittest
from unittest.mock import Mock, patch

import pytest


@pytest.mark.usefixtures("instruqt_xblock")
class TestInstruqtXBlock(unittest.TestCase):

    def test_student_view(self):
        """ Test content of InstuqtXBlock's student view """
        student_fragment = self.instruqt_xblock.render('student_view', Mock())
        self.assertIn('<div class="instruqtxblock_block">', student_fragment.content)
        self.assertIn('<iframe', student_fragment.content)

    def test_completion_handler_on_track_completed(self):
        """ Test completion_handler method when track is completed """
        request_body = b"""{
            "event": "track.completed",
            "params": {
                "track_slug": "container-test",
                "challenge_slug": "creating-a-directory"
            }
        }"""
        request = Mock(method='POST', body=request_body)
        response = self.instruqt_xblock.completion_handler(request)

        expected_response_json = {
            "result": {
                "save_track_completion": True,
                "save_challenge_completion": False,
            }
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.dumps(response.json), json.dumps(expected_response_json))

    def test_completion_handler_on_challege_completed(self):
        """ Test completion_handler method when challenge is completed """
        request_body = b"""{
            "event": "track.challenge_completed",
            "params": {
                "track_slug": "container-test",
                "challenge_slug": "creating-a-directory",
                "total_challenges": 3
            }
        }"""
        request = Mock(method='POST', body=request_body)
        response = self.instruqt_xblock.completion_handler(request)

        expected_response_json = {
            "result": {
                "save_track_completion": False,
                "save_challenge_completion": True,
            }
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.dumps(response.json), json.dumps(expected_response_json))

    @patch("instruqtxblock.instruqtxblock.log.error")
    def test_completion_handler_on_missing_key(self, mock_err_log):
        """ Test completion_handler method when challenge is completed but withour a required key """
        request_body = b"""{
            "event": "track.challenge_completed",
            "params": {
                "track_slug": "container-test",
                "challenge_slug": "creating-a-directory"
            }
        }"""
        request = Mock(method='POST', body=request_body)
        response = self.instruqt_xblock.completion_handler(request)

        expected_response_json = {
            "result": {
                "save_track_completion": False,
                "save_challenge_completion": False,
            }
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.dumps(response.json), json.dumps(expected_response_json))
        mock_err_log.assert_called_once()
        self.assertEqual(mock_err_log.call_args[0][0], 'Error while marking challenge completion %s')

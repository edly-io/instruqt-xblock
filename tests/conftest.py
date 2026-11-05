"""
Fixtures for test cases
"""

from unittest.mock import Mock

import pytest
from workbench.runtime import WorkbenchRuntime
from xblock.fields import ScopeIds
from xblock.runtime import DictKeyValueStore, KvsFieldData

from instruqtxblock.instruqtxblock import InstruqtXBlock


def generate_scope_ids(runtime, block_type):
    """ helper to generate scope IDs for an XBlock """
    def_id = runtime.id_generator.create_definition(block_type)
    usage_id = runtime.id_generator.create_usage(def_id)
    return ScopeIds('user', block_type, def_id, usage_id)


def make_block():
    """Build an InstruqtXBlock backed by an in-memory workbench runtime."""
    runtime = WorkbenchRuntime()
    db_model = KvsFieldData(DictKeyValueStore())
    ids = generate_scope_ids(runtime, 'instruqtxblock')
    block = InstruqtXBlock(runtime, db_model, scope_ids=ids)
    block.usage_id = Mock()
    return block


@pytest.fixture(scope="class")
def instruqt_xblock(request):
    """Instruct XBlock pytest fixture."""
    instruqt_xblock = make_block()
    instruqt_xblock.has_score = True
    request.cls.instruqt_xblock = instruqt_xblock


@pytest.fixture
def block():
    """Fresh InstruqtXBlock per test."""
    return make_block()

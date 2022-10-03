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


@pytest.fixture(scope="class")
def instruqt_xblock(request):
    """Instruct XBlock pytest fixture."""
    runtime = WorkbenchRuntime()
    key_store = DictKeyValueStore()
    db_model = KvsFieldData(key_store)
    ids = generate_scope_ids(runtime, 'instruqtxblock')
    instruqt_xblock = InstruqtXBlock(runtime, db_model, scope_ids=ids)
    instruqt_xblock.usage_id = Mock()
    instruqt_xblock.has_score = True
    request.cls.instruqt_xblock = instruqt_xblock

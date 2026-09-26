import pytest
import os

def pytest_collection_modifyitems(config, items):
    """Skip integration and infogami tests to avoid external dependencies.
    This hook marks any test located under the 'tests/integration' directory
    or under the 'infogami' package as skipped.
    """
    skip_marker = pytest.mark.skip(reason="Skipping external dependency tests (integration/infogami)")
    integration_path = os.path.abspath('tests/integration')
    infogami_path = os.path.abspath('infogami')
    for item in items:
        fp = os.path.abspath(str(item.fspath))
        if integration_path in fp or infogami_path in fp:
            item.add_marker(skip_marker)

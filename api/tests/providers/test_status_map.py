import os
from api.app.status_map import load_status_map, canonical_status


def test_canonical_status_mapping_phaxio(tmp_path):
    # Ensure map loads from repo config
    load_status_map()
    assert canonical_status('phaxio', 'queued') == 'queued'
    assert canonical_status('phaxio', 'processing') == 'in_progress'
    assert canonical_status('phaxio', 'success') == 'success'
    assert canonical_status('phaxio', 'error') == 'failed'


def test_canonical_status_mapping_sinch():
    load_status_map()
    assert canonical_status('sinch', 'queued') == 'queued'
    assert canonical_status('sinch', 'processing') == 'in_progress'
    assert canonical_status('sinch', 'completed_ok') == 'success'
    assert canonical_status('sinch', 'failure') == 'failed'


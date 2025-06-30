import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
from stix2arango.stix2arango.stix2arango import Stix2Arango


def test_is_large_file():
    s2a = Stix2Arango(
        file="some-file",
        database="s2a_tests",
        collection="test_run",
        is_large_file=True,
    )
    with (
        patch("stix2arango.stix2arango.stix2arango.BundleLoader") as mock_bundle_loader,
        patch.object(Stix2Arango, "run_with_bundle") as mock_run_with_bundle,
    ):
        mocked_bundle = mock_bundle_loader.return_value
        mocked_bundle.chunks = [1, 2, 3]
        mocked_bundle.bundle_id = "my-bundle"
        s2a.run()
        mock_run_with_bundle.assert_has_calls(
            [
                call(dict(type="bundle", objects=x, id="my-bundle"))
                for x in mock_bundle_loader.return_value.chunks
            ]
        )


def test_file_normal():
    data = {"type": "bundle", "id": "some-id", "objects": []}
    f = Path("some-file")
    f.write_text(json.dumps(data))
    s2a = Stix2Arango(
        file=f.name, database="s2a_tests", collection="test_run", is_large_file=False
    )
    with (
        patch("stix2arango.stix2arango.stix2arango.BundleLoader") as mock_bundle_loader,
        patch.object(Stix2Arango, "run_with_bundle") as mock_run_with_bundle,
    ):
        s2a.run()
        mock_bundle_loader.assert_not_called()
        mock_run_with_bundle.assert_called_once_with(data)


def test_add_object_alter_fn():
    s2a = Stix2Arango(
        file='', database="s2a_tests", collection="test_run", is_large_file=False
    )
    with pytest.raises(ValueError):
        s2a.add_object_alter_fn(None)

    with pytest.raises(ValueError):
        s2a.add_object_alter_fn(['some', 'array', 1])

def test_alter_functions():
    s2a = Stix2Arango(
        file='', database="s2a_tests", collection="test_run", is_large_file=False
    )
    fn1 = MagicMock()
    fn2 = MagicMock()
    fn3 = lambda x: 1/0
    bundle = {"type": "bundle", "id": "some-id", "objects": [{'id': 'obj--1', 'type': 'some-type'}, {'id': 'obj--2', 'type': 'some-type'}]}
    s2a.add_object_alter_fn(fn1)
    s2a.add_object_alter_fn(fn2)
    s2a.add_object_alter_fn(fn3)
    s2a.run(data=bundle)
    fn1.assert_has_calls([call(x) for x in bundle['objects']], any_order=True)
    fn2.assert_has_calls([call(x) for x in bundle['objects']], any_order=True)

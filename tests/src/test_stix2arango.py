import json
import os
from pathlib import Path
from unittest.mock import patch, call
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

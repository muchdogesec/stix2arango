import sys
from unittest.mock import patch
import pytest
from stix2arango.__main__ import parse_arguments, main


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--database", "somedb"],
        ["--file", "somefile"],
        ["--file", "somefile", "--database", "somedb"],
        ["--collection", "somefile", "--database", "somedb"],
    ],
)
def test_database_and_file_required(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["prog", *args])
    with pytest.raises(SystemExit) as e:
        parse_arguments()


@pytest.mark.parametrize(
    "args,parsed_output",
    [
        (
            ["--collection", "somefile", "--database", "somedb", "--file", "some-file"],
            {
                "file": "some-file",
                "is_large_file": False,
                "database": "somedb",
                "create_db": True,
                "collection": "somefile",
                "stix2arango_note": "",
                "ignore_embedded_relationships": False,
                "ignore_embedded_relationships_sro": False,
                "ignore_embedded_relationships_smo": False,
                "include_embedded_relationships_attributes": None,
            },
        ),
        (
            [
                "--collection",
                "somefile",
                "--database",
                "somedb",
                "--file",
                "some-file",
                "--ignore_embedded_relationships_smo",
                "yes",
            ],
            {
                "file": "some-file",
                "is_large_file": False,
                "database": "somedb",
                "create_db": True,
                "collection": "somefile",
                "stix2arango_note": "",
                "ignore_embedded_relationships": False,
                "ignore_embedded_relationships_sro": False,
                "ignore_embedded_relationships_smo": True,
                "include_embedded_relationships_attributes": None,
            },
        ),
        (
            [
                "--collection",
                "somefile",
                "--database",
                "somedb",
                "--file",
                "some-file",
                "--ignore_embedded_relationships_smo",
                "yes",
                "--include_embedded_relationships_attributes",
                "abc_ref",
                "abcdef_refs",
            ],
            {
                "file": "some-file",
                "is_large_file": False,
                "database": "somedb",
                "create_db": True,
                "collection": "somefile",
                "stix2arango_note": "",
                "ignore_embedded_relationships": False,
                "ignore_embedded_relationships_sro": False,
                "ignore_embedded_relationships_smo": True,
                "include_embedded_relationships_attributes": ["abc_ref", "abcdef_refs"],
            },
        ),
    ],
)
def test_parse_args(monkeypatch, args, parsed_output):
    args = ["prog", *args]
    monkeypatch.setattr(sys, "argv", args)
    assert parse_arguments().__dict__ == parsed_output


def test_main_calls_correctly(monkeypatch):
    args = [
        "prog",
        "--collection",
        "somefile",
        "--database",
        "somedb",
        "--file",
        "some-file",
        "--ignore_embedded_relationships_smo",
        "yes",
        "--include_embedded_relationships_attributes",
        "abc_ref",
        "abcdef_refs",
    ]
    monkeypatch.setattr(sys, "argv", args)
    with patch("stix2arango.__main__.Stix2Arango") as mock_s2a_init:
        main()
        mock_s2a_init.assert_called_once_with(
            **{
                "file": "some-file",
                "is_large_file": False,
                "database": "somedb",
                "create_db": True,
                "collection": "somefile",
                "stix2arango_note": "",
                "ignore_embedded_relationships": False,
                "ignore_embedded_relationships_sro": False,
                "ignore_embedded_relationships_smo": True,
                "include_embedded_relationships_attributes": ["abc_ref", "abcdef_refs"],
            }
        )

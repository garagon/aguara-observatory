"""Tests for utility functions."""

from crawlers.utils import content_hash, shard_matches


def test_content_hash_string():
    h = content_hash("hello world")
    assert len(h) == 64  # SHA-256 hex
    # Same content, same hash
    assert content_hash("hello world") == h


def test_content_hash_bytes():
    h = content_hash(b"hello world")
    assert len(h) == 64
    # Should match string version
    assert content_hash("hello world") == h


def test_shard_matches():
    assert shard_matches("apple", "A-F") is True
    assert shard_matches("banana", "A-F") is True
    assert shard_matches("fig", "A-F") is True
    assert shard_matches("grape", "A-F") is False
    assert shard_matches("grape", "G-L") is True
    assert shard_matches("mango", "M-R") is True
    assert shard_matches("zebra", "S-Z") is True

    # Edge cases
    assert shard_matches("Apple", "A-F") is True  # case insensitive
    assert shard_matches("", "A-F") is True  # empty slug
    assert shard_matches("test", "") is True  # empty shard
    assert shard_matches("test", None) is True  # no shard

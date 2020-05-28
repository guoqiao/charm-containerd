import os
import json
from unittest.mock import patch
from charmhelpers.core import unitdata
from reactive import containerd
import tempfile


def test_merge_custom_registries():
    """Verify merges of registries."""
    with tempfile.TemporaryDirectory() as dir:
        config = [{
            "url": "my.registry:port",
            "username": "user",
            "password": "pass"
        }, {
            "url": "my.other.registry",
            "ca_file": "aGVsbG8gd29ybGQgY2EtZmlsZQ==",
            "key_file": "aGVsbG8gd29ybGQga2V5LWZpbGU=",
        }]
        ctxs = containerd.merge_custom_registries(dir, json.dumps(config))
        with open(os.path.join(dir, "my.other.registry.ca")) as f:
            assert f.read() == "hello world ca-file"
        with open(os.path.join(dir, "my.other.registry.key")) as f:
            assert f.read() == "hello world key-file"
        assert not os.path.exists(os.path.join(dir, "my.other.registry.cert"))

        for ctx in ctxs:
            assert 'url' in ctx


def test_juju_proxy_changed():
    """Verify proxy changed bools are set as expected."""
    cached = {'http_proxy': 'foo', 'https_proxy': 'foo', 'no_proxy': 'foo'}
    new = {'http_proxy': 'bar', 'https_proxy': 'bar', 'no_proxy': 'bar'}

    # Test when nothing is cached
    db = unitdata.kv()
    db.get.return_value = None
    assert containerd._juju_proxy_changed() is True

    # Test when cache hasn't changed
    db.get.return_value = cached
    with patch('reactive.containerd.check_for_juju_https_proxy',
               return_value=cached):
        assert containerd._juju_proxy_changed() is False

    # Test when cache has changed
    db.get.return_value = cached
    with patch('reactive.containerd.check_for_juju_https_proxy',
               return_value=new):
        assert containerd._juju_proxy_changed() is True

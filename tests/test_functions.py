import os.path as op
from scuts.utils import hash_file


def test_hash_file():
    text_test_path = op.join(op.dirname(__file__), 'test_ressources/test_file.txt')
    assert hash_file(text_test_path) == 'f0c90f3af3f5c7ec3eda05e919385ec67716d9db0ac94eb0c3846139f8d7520a'


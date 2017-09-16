# -*- coding: utf-8 -*-
__author__ = "msidolphin"
import hashlib


def get_md5(source):
    if isinstance(source, str):
        source = source.encode("utf-8")
    # import _md5
    m = hashlib.md5()
    m.update(source)
    return m.hexdigest()


if __name__ == '__main__':
    pass
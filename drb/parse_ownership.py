# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from drb.dbc import precondition

def parse_ownership(ownership):
    try:
        uid, gid = [int(x) for x in ownership.strip().split(":")]
        precondition(uid >= 0, "uid must be >= 0")
        precondition(gid >= 0, "gid must be >= 0")
        return uid, gid
    except:
        raise ValueError("Invalid ownership string '{0}'".format(ownership))

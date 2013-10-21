# -*- coding: utf-8 -*-
"""
    glusternodestate.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, GPL v2, see LICENSE for more details.
"""

import argparse
import errno
import os
from functools import wraps
import sys

from glusterfstools import volumes
import nodestatedb as _db


DB_PATH = "/var/lib/glusterd/nodestate/"
DB_FILE = DB_PATH + "glusternodestate.db"
HOOKS_ROOT = "/var/lib/glusterd/hooks/1/"
_glusterfs_events_funcs = {}


class GlusterNodeStateError(Exception):
    pass


def _get_args():
    parser = argparse.ArgumentParser(description='Handle GlusterFS state')
    parser.add_argument('event')
    parser.add_argument('--volname', type=str, help='volume name')
    parser.add_argument('--first', type=str, help='Dont know yet')
    parser.add_argument('--last', type=str, help='Dont know yet')
    return parser.parse_args()


def glusterfsevent(name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            return f(*args, **kwds)

        global _glusterfs_events_funcs
        _glusterfs_events_funcs[name] = wrapper
        return wrapper
    return decorator


@glusterfsevent("setup")
def setup(param=None):
    os.mkdir(DB_PATH)
    _db.connect(DB_FILE)
    _db.setup()
    os.chown(DB_FILE, 0, 0)
    os.chmod(DB_FILE, 0600)
    sys.stdout.write("Created DB: %s\n" % DB_FILE)
    events = ["add-brick", "create", "delete",
              "remove-brick", "set", "start", "stop"]

    for event in events:
        hook_file = HOOKS_ROOT + "%s/post/Sglusternodestate.bash" % event
        with open(hook_file, "w") as f:
            f.write("#!/bin/bash\nglusternodestate %s \"$@\"" % event)
            sys.stdout.write("Added Hook: %s\n" % hook_file)
        os.chmod(hook_file, 0755)


@glusterfsevent("cleanup")
def cleanup(param=None):
    try:
        os.remove(DB_FILE)
        sys.stdout.write("removed DB file\n")
        os.rmdir(DB_PATH)
        events = ["add-brick", "create", "delete",
                  "remove-brick", "set", "start", "stop"]

        for event in events:
            hook_file = HOOKS_ROOT + "%s/post/Sglusternodestate.bash" % event
            os.remove(hook_file)
            sys.stdout.write("removed Hook file: %s\n" % hook_file)
    except (IOError, OSError):
        if sys.exc_info()[1].errno == errno.ENOENT:
            pass
        else:
            raise GlusterNodeStateError('Error while cleanup')


@glusterfsevent("glusterd-start")
def flush_and_regenerate(param=None):
    _db.table_cleanup_all()
    vols = []
    vols_data = volumes.get()

    for vol in vols_data:
        bricks = []
        vols.append((vol["uuid"],
                     vol["name"],
                     vol["type"],
                     vol["status"],
                     vol["num_bricks"],
                     vol["transport"]))

        for brick in vol['bricks']:
            bricks.append((vol['name'], brick))

    _db.volumes_add(vols)
    _db.bricks_add(bricks)


@glusterfsevent("create")
def volume_create(volume):
    vol_data = volumes.get(volume)
    vol_data = vol_data[0]
    vol = (vol["uuid"],
           vol["name"],
           vol["type"],
           vol["status"],
           vol["num_bricks"],
           vol["transport"])

    _db.volumes_add([vols])
    bricks = []
    for brick in vol['bricks']:
        bricks.append((vol['name'], brick))

    _db.bricks_add(bricks)


@glusterfsevent("delete")
def volume_delete(volume):
    _db.table_cleanup_all(volume=volume)


@glusterfsevent("add-brick")
def add_brick(volume):
    add_remove_brick(volume, "add")


@glusterfsevent("remove-brick")
def remove_brick(volume):
    add_remove_brick(volume, "add")


def add_remove_brick(volume, action):
    _db.table_cleanup_bricks(volume=volume)

    vol_data = volumes.get(volume)
    vol = vol_data[0]

    bricks = []
    for brick in vol['bricks']:
        bricks.append((vol['name'], brick))

    _db.bricks_add(bricks)
    _db.update_volume(vol['name'], "num_bricks", len(bricks))


@glusterfsevent("set")
def options_set(volume):
    _db.table_cleanup_options(volume)
    vol_data = volumes.get(volume)
    vol = vol_data[0]

    options = []
    for opt in vol['options']:
        options.append((vol['name'], opt['name'], opt['value']))

    _db.options_add(options)


@glusterfsevent("start")
def volume_start(volume):
    _db.update_volume(volume, "status", "UP")


@glusterfsevent("stop")
def volume_stop(volume):
    _db.update_volume(volume, "status", "DOWN")


def main():
    args = _get_args()

    if not args.event in ["setup", "cleanup"]:
        _db.connect(DB_FILE)

    if args.event in _glusterfs_events_funcs:
        _glusterfs_events_funcs[args.event](args.volname)


if __name__ == "__main__":
    main()

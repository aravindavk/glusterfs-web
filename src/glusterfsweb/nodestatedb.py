# -*- coding: utf-8 -*-
"""
    nodestatedb.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, GPL v2, see LICENSE for more details.
"""

import sqlite3

conn = None
cursor = None


def connect(db_file):
    global conn, cursor
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()


def get_volumes():
    volumes = []
    query = "SELECT name, type, status, num_bricks FROM volumes"
    for row in cursor.execute(query):
        volumes.append({"name": row[0],
                        "type": row[1],
                        "status": row[2],
                        "num_bricks": row[3]})
    return volumes


def table_cleanup_volumes(volume=None):
    query = "DELETE FROM volumes"

    if volume:
        query += " WHERE name = ?"
        cursor.execute(query, (volume,))
    else:
        cursor.execute(query)

    conn.commit()


def table_cleanup_bricks(volume=None):
    query = "DELETE FROM bricks"

    if volume:
        query += " WHERE volume = ?"
        cursor.execute(query, (volume,))
    else:
        cursor.execute(query)

    conn.commit()


def table_cleanup_options(volume=None):
    query = "DELETE FROM options"

    if volume:
        query += " WHERE volume = ?"
        cursor.execute(query, (volume,))
    else:
        cursor.execute(query)

    conn.commit()


def table_cleanup_all(volume=None):
    table_cleanup_volumes(volume)
    table_cleanup_bricks(volume)
    table_cleanup_options(volume)


def volumes_add(vols):
    query = """INSERT INTO volumes(id, name, type, status, num_bricks,
    transport, updated_at) VALUES(?, ?, ?, ?, ?, ?, datetime('now'))"""

    cursor.executemany(query, vols)
    conn.commit()


def bricks_add(bricks):
    query = """INSERT INTO bricks(volume, brick, updated_at)
    VALUES(?, ?, datetime('now'))"""
    cursor.executemany(query, bricks)
    conn.commit()


def options_add(options):
    query = """INSERT INTO options(volume, name, value, updated_at)
    VALUES(?, ?, ?, datetime('now'))"""
    cursor.executemany(query, options)
    conn.commit()


def update_volume(volume, key, value):
    query = """UPDATE volumes SET %s = ?, updated_at = datetime('now')
    WHERE name = ?""" % key
    cursor.execute(query, (value, volume))
    conn.commit()


def setup():
    queries = ["DROP TABLE IF EXISTS volumes",
               "DROP TABLE IF EXISTS bricks",
               """CREATE TABLE volumes(
               id VARCHAR(40),
               name VARCHAR(100),
               type VARCHAR(20),
               status VARCHAR(10),
               transport VARCHAR(20),
               num_bricks INT,
               updated_at DATETIME,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
               )
               """,
               """CREATE TABLE bricks(
               volume VARCHAR(100),
               brick VARCHAR(200),
               status VARCHAR(10),
               updated_at DATETIME,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
               )
               """,
               """CREATE TABLE options(
               volume VARCHAR(100),
               key VARCHAR(500),
               value VARCHAR(500),
               updated_at DATETIME,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
               )
               """]
    for query in queries:
        cursor.execute(query)

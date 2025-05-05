# -*- coding: utf-8 -*-
import sqlite3


def addBarcode(bdata, btype):
    with sqlite3.connect("allCodes.db") as conn:
        cursor = conn.cursor()
        # Insert the code into the database
        cursor.execute(
            'INSERT INTO codes(code, type) VALUES(?, ?)', (bdata, btype))
        conn.commit()

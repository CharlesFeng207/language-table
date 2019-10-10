# coding: utf-8
import pymysql
import sys
import uuid
import requests
import hashlib
import time
import json
import Language_pb2
import model
import time
from zhconv import convert

if __name__ == "__main__":
    db = pymysql.connect("localhost", "root", "", "language")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM language;")
    result = cursor.fetchall()
    cursor.close()
    db.close()

    pending = []
    for data in result:
        for lantype in Language_pb2.LanguageType.values():
            if lantype != Language_pb2.zh:
                continue

            t = data[lantype+1]
            # if not t:
            pending.append((data[0], data[1], lantype))y

    # print(pending)

    if input("press y to continue...") == "y":
        for lanId, chtext, lanType in pending:
            t = convert(chtext, "zh-tw")
            print(lanId, t)
            model.edit_txt(lanId, lanType, t)
            # time.sleep(0.05)
        pass

    pass

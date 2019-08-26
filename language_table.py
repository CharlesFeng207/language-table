# coding:utf-8
from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from flask import Flask, render_template, flash, request, redirect, url_for, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from time import sleep
import random
import datetime
import os
import Language_pb2
from Language_pb2 import LanguageTable, LanguageInfo
import json
from logger_init import LoggerInit
import logging

class Table:
    def __init__(self):
        self.error_txt = None
        self.table_dic = {}  # cn -> id
        self.max_id_value = 0
        self.max_row = 0
        self.id_start_row = 3

    def load(self, path, shert_name):
        self.path_src = path
        logging.info("loading {}".format(self.path_src))

        try:
            self.workbook_src = load_workbook(self.path_src, data_only=True)
            self.sheet_src = self.workbook_src[shert_name]
            self.max_row = self.sheet_src.max_row
            for i in range(self.id_start_row, self.max_row + 1):
                cn_value = self.get_lan(i,  Language_pb2.ch)
                id_value = self.get_id(i)
                self.max_id_value = max(self.max_id_value, id_value)
                if cn_value in self.table_dic:
                    self.error_txt = "简体中文 \"{}\" 存在重复！".format(cn_value)
                    break
                self.table_dic[cn_value] = id_value
            print("load complete!")
        except Exception as e:
            self.error_txt = "解析excel表时报错! {}".format(e)

        print(self.error_txt)

    def insert(self, cn, save=True):
        if save:
            self.workbook_src.save("backup")

        newid = self.max_id_value + 1
        self.table_dic[cn] = newid
        self.max_id_value += 1
        self.max_row += 1

        self.sheet_src["{}{}".format('B', self.max_row)].value = cn
        self.sheet_src["{}{}".format('A', self.max_row)].value = newid

        if save:
            self.workbook_src.save(self.path_src)

        return newid

    def get_lan(self, row, lanType):
        col = get_column_letter(lanType+2)  # cn 2 en 3 zh 4 jp 5 ko 6
        value = self.sheet_src["{}{}".format(col, row)].value
        return str(value) if value is not None else ""

    def get_id(self, row):
        return self.sheet_src["{}{}".format('A', row)].value

LoggerInit.init(level=logging.INFO, filemode='a')
table = Table()
app = Flask(__name__)


class MyForm(Form):
    username = TextField('简体中文 -> id：', [])


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if table.error_txt is not None:
        return table.error_txt

    copy_text = None
    form = MyForm(request.form)
    if request.method == 'POST' and form.validate():

        flash_info = None

        if not form.username.data:
            flash_info = "输入为空"
        else:
            if form.username.data in table.table_dic:
                flash_info = "存在 \"{}\"，id为{}".format(
                    form.username.data, table.table_dic[form.username.data])
                copy_text = table.table_dic[form.username.data]
            else:
                copy_text = table.insert(form.username.data)
                flash_info = "录入 \"{}\"，id为{}".format(
                    form.username.data, table.table_dic[form.username.data])

        flash(flash_info)
        # return redirect(url_for('hello'))
    info = "正在托管{}，当前文本数量: {}".format(table.path_src, len(table.table_dic))
    return render_template('hello.html', form=form, info=info, copy_text=copy_text)


@app.route('/query')
def query():
    content = request.args.get('content')
    save = request.args.get('save') == "1"

    if content in table.table_dic:
        return str(table.table_dic[content])
    else:
        return str(table.insert(content, save))


@app.route('/getexcel')
def getexcel():
    return send_file(table.path_src, cache_timeout=-1, as_attachment=True)


@app.route('/getbytes')
def getbytes():
    bytes_path = "language.bytes"
    proto_table = LanguageTable()

    for i in range(table.id_start_row, table.sheet_src.max_row + 1):
        info = LanguageInfo()

        info.id = table.get_id(i)
        for lantype in Language_pb2.LanguageType.values():
            s = table.get_lan(i, lantype)
            info.content.append(s)
        print(info)
        print(info.content)
        proto_table.infos.append(info)

    print(proto_table)

    with open(bytes_path, "wb+") as f:
        f.write(proto_table.SerializeToString())

    return send_file(bytes_path, cache_timeout=-1, as_attachment=True)


@app.route('/getjson')
def getjson():
    json_path = "language.json"
    json_table = {}

    for i in range(table.id_start_row, table.sheet_src.max_row + 1):
        info = {}

        info["id"] = table.get_id(i)
        info["content"] = []

        for lantype in Language_pb2.LanguageType.values():
            info["content"].append(table.get_lan(i, lantype))

        json_table[info["id"]] = info

    with open(json_path, "w+") as f:
        f.write(json.dumps(json_table, ensure_ascii=False))

    return send_file(json_path, cache_timeout=-1, as_attachment=True)


@app.route('/test')
def test():
    bytes_path = "language.bytes"
    with open(bytes_path, "rb") as f:
        proto_table = LanguageTable()
        proto_table.ParseFromString(f.read())
        return str(proto_table)

    # for i in range(0, 5000):
    #     table.insert("form.username.data {}".format(table.max_id_value + 1), False)
    return "done"


def mytest():
    bytes_path = "language.bytes"
    proto_table = LanguageTable()

    for i in range(table.id_start_row, table.sheet_src.max_row + 1):
        info = LanguageInfo()

        info.id = table.get_id(i)
        for lantype in Language_pb2.LanguageType.values():
            info.content.append(table.get_lan(i, lantype))
        proto_table.infos.append(info)

    with open(bytes_path, "wb+") as f:
        f.write(proto_table.SerializeToString())


if __name__ == '__main__':
    os.system("python --version")
    table.load("Language.xlsx", "Language")
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = 'some_secret'
    app.run(debug=True, host="0.0.0.0", threaded=True, processes=0)

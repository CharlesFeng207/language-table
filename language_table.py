# coding:utf-8
from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from flask import Flask, render_template, flash, request, redirect, url_for, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators, IntegerField
from time import sleep
import random
import datetime
import os
import Language_pb2
from Language_pb2 import LanguageTable, LanguageInfo
import json
from logger_init import LoggerInit
import logging
from google.protobuf import text_format
import shutil
import requests


class Table:
    def __init__(self):
        self.error_txt = None
        self.table_dic = {}  # cn -> id
        self.max_id_value = 0
        self.max_row = 0
        self.id_start_row = 3
        self.backup_order = 0
        self.max_backup_count = 30
        self.backup_folder = "backup"

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
            logging.info("load complete!")
        except Exception as e:
            self.error_txt = "解析excel表时报错! {}".format(e)

        logging.error(self.error_txt)

    def insert(self, cn):
        newid = self.max_id_value + 1

        self.table_dic[cn] = newid
        self.max_id_value += 1
        self.max_row += 1

        self.sheet_src["{}{}".format('B', self.max_row)].value = cn
        self.sheet_src["{}{}".format('A', self.max_row)].value = newid

        return newid

    def remove(self, cn):
        if cn not in self.table_dic:
            return

        lanId = self.table_dic[cn]

        del self.table_dic[cn]

        for i in range(self.id_start_row, self.max_row + 1):
            id_value = self.get_id(i)
            if id_value == lanId:
                self.sheet_src.delete_rows(i, 1)
                break

        self.max_row = self.sheet_src.max_row

    def change(self, lanId, cn):
        for i in range(self.id_start_row, self.max_row + 1):
            id_value = self.get_id(i)
            if id_value == lanId:
                self.sheet_src["{}{}".format('B', i)].value = cn

    def save(self):
        # backup first
        if not os.path.exists(self.backup_folder):
            os.mkdir(self.backup_folder)
            shutil.copy(self.path_src, os.path.join(
                self.backup_folder, str(self.backup_order)))
            self.backup_order = (self.backup_order + 1) % self.max_backup_count

        self.workbook_src.save(self.path_src)

    def get_lan(self, row, lanType):
        col = get_column_letter(lanType+2)  # cn 2 en 3 zh 4 jp 5 ko 6
        value = self.sheet_src["{}{}".format(col, row)].value
        return str(value) if value is not None else ""

    def get_id(self, row):
        print(row)
        return int(self.sheet_src["{}{}".format('A', row)].value)
    pass


pass


class MyForm(Form):
    inputText = TextField('', [])
    inputId = TextField('', [])

# a hacky way to get but don't wait:
def save_not_wait():
    try:
        requests.get("http://127.0.0.1:{}/save".format(flask_port),
                     timeout=0.0000000001)
    except requests.exceptions.ReadTimeout:
        pass


def save_history(info):
    with open("history.txt", "a+") as f:
        f.write(
            "{} {}</br>\n".format(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), info))


app = Flask(__name__)

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@app.route('/hello2', methods=['GET', 'POST'])
def hello():
    if table.error_txt is not None:
        return table.error_txt

    form = MyForm(request.form)
    print(request.form)

    if request.method == 'POST' and form.validate():

        flash_info = None

        if "录入简体中文" in request.form or "查询简体中文" in request.form:
            if not form.inputText.data:
                flash_info = "text输入为空"
            else:
                if form.inputText.data in table.table_dic:
                    flash_info = "存在 \"{}\"，id为{}".format(
                        form.inputText.data, table.table_dic[form.inputText.data])
                    form.inputId.data = table.table_dic[form.inputText.data]
                else:
                    if "录入简体中文" in request.form:
                        form.inputId.data = table.insert(form.inputText.data)
                        flash_info = "录入 \"{}\"，id为{}".format(
                            form.inputText.data, table.table_dic[form.inputText.data])
                        save_history(flash_info)
                        save_not_wait()
                    else:
                        flash_info = "\"{}\" 不存在!".format(form.inputText.data)
                pass
            pass
        elif "查询ID" in request.form or "删除ID"in request.form or "编辑ID" in request.form:
            if not form.inputId.data:
                flash_info = "id输入为空"
            elif not representsInt(form.inputId.data):
                 flash_info = "请输入int类型"
            else:
                query_result = None
                form_id = int(form.inputId.data)

                for cn, id in table.table_dic.items():
                    if id == form_id:
                        query_result = cn
                        break
                if query_result is None:
                    flash_info = "id {} 未找到".format(form_id)
                else:
                    flash_info = "id:{} -> \"{}\"".format(id, query_result)
                    if "编辑ID" in request.form:
                        if not form.inputText.data:
                            flash_info = "text输入为空"
                        elif form.inputText.data in table.table_dic:
                             flash_info = "存在 \"{}\"，id为{}".format(
                                 form.inputText.data, table.table_dic[form.inputText.data])
                        else:
                            flash_info = "编辑 {} -> {} -> {}".format(
                                form_id, query_result, form.inputText.data)
                            table.change(form_id, form.inputText.data)
                            save_history(flash_info)
                            save_not_wait()
                    elif "删除ID" in request.form:
                        table.remove(query_result)
                        flash_info = "删除 " + flash_info
                        save_history(flash_info)
                        save_not_wait()
                    pass
                pass
            pass
        

        flash(flash_info)

    info = "正在托管{}，文本数量: {} 最高行数: {} 最大ID: {}".format(table.path_src, len(table.table_dic), table.max_row, table.max_id_value)
    return render_template('hello.html', myform=form, info=info)


@app.route('/query2')
def query():
    content = request.args.get('content')
    save = request.args.get('save') == "1"

    result = None
    if content in table.table_dic:
        result = str(table.table_dic[content])
    else:
        result = str(table.insert(content))

    if save:
        save_not_wait()

    return result


@app.route('/history')
def history():
    content = "None"
    if os.path.exists("history.txt"):
        with open("history.txt", "r") as f:
            content = f.read()

    return content


@app.route('/save')
def save():
    table.save()
    return "done"


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
            info.content.append(s.encode('utf-8'))
        proto_table.infos.append(info)

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
    # bytes_path = "language.bytes"
    # with open(bytes_path, "rb") as f:
    #     proto_table = LanguageTable()
    #     proto_table.ParseFromString(f.read())
    #     return text_format.MessageToString(proto_table)

    # for i in range(0, 5000):
    #     table.insert("form.username.data {}".format(table.max_id_value + 1), False)
    return "done"


flask_port = 5000
LoggerInit.init(level=logging.INFO, filemode='a')
table = Table()

if __name__ == "__main__":
    table.load("Language.xlsx", "Language")
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = 'some_secret'
    app.run(debug=True, host="0.0.0.0", threaded=False, processes=0, port=5000)

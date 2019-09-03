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
import requests
from table import Table


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

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if table.error_txt is not None:
        return table.error_txt

    form = MyForm(request.form)

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
                query_cn = None
                form_id = int(form.inputId.data)

                for cn, id in table.table_dic.items():
                    if id == form_id:
                        query_cn = cn
                        break
                if query_cn is None:
                    flash_info = "id {} 未找到".format(form_id)
                else:
                    flash_info = "id:{} -> \"{}\"".format(id, query_cn)
                    if "编辑ID" in request.form:
                        if not form.inputText.data:
                            flash_info = "text输入为空"
                        elif form.inputText.data in table.table_dic:
                             flash_info = "存在 \"{}\"，id为{}".format(
                                 form.inputText.data, table.table_dic[form.inputText.data])
                        else:
                            flash_info = "编辑 {} -> {} -> {}".format(
                                form_id, query_cn, form.inputText.data)
                            table.change(form_id, query_cn, form.inputText.data, Language_pb2.ch)
                            save_history(flash_info)
                            save_not_wait()
                    elif "删除ID" in request.form:
                        table.remove(query_cn)
                        flash_info = "删除 " + flash_info
                        save_history(flash_info)
                        save_not_wait()
                    pass
                pass
            pass
        

        flash(flash_info)

    info = "正在托管{}，文本数量: {} 最高行数: {} 最大ID: {}".format(table.path_src, len(table.table_dic), table.max_row, table.max_id_value)
    return render_template('hello.html', myform=form, info=info)


@app.route('/query')
def query():
    content = request.args.get('content')
    save = request.args.get('save') == "1"

    result = None
    if content in table.table_dic:
        result = str(table.table_dic[content])
    else:
        result = str(table.insert(content))
        save_history("录入 \"{}\"，id为{}, from query save:{}".format(content, result, save))

    if save:
        save_not_wait()

    return result
    
@app.route('/edit')
def edit():
    lanId = int(request.args.get('id'))
    content = request.args.get('content')
    lanType = int(request.args.get('lanType'))

    query_cn = None
    for cn, id in table.table_dic.items():
        if id == lanId:
            query_cn = cn
            break
            
    if query_cn is None:
        return "id未能找到"

    table.change(lanId, query_cn, content, lanType)

    save_history("编辑 {} -> {} -> {}, from edit lanType:{}".format(lanId, query_cn, content, lanType))
    save_not_wait()

    return "成功"


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
            if info.id != 0 and s == "":
                s = "[{}没填翻译!] {}".format(info.id, table.get_lan(i, Language_pb2.ch))
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

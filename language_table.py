# coding:utf-8
import model
from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from flask import Flask, render_template, flash, request, redirect, url_for, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators, IntegerField
import os
import Language_pb2
from Language_pb2 import LanguageTable, LanguageInfo
import json
from logger_init import LoggerInit
import logging
from google.protobuf import text_format
import requests


class MyForm(Form):
    inputText = TextField('', [])
    inputId = TextField('', [])


app = Flask(__name__)


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    form = MyForm(request.form)

    if request.method == 'POST' and form.validate():
        flash_info = None
        if "录入简体中文" in request.form or "查询简体中文" in request.form:
            if not form.inputText.data:
                flash_info = "text输入为空"
            else:
                result = model.query_id(form.inputText.data)
                if result != -1:
                     flash_info = "存在 \"{}\"，id为{}".format(
                         form.inputText.data, result)
                    form.inputId.data = str(result)
                else:
                    if "录入简体中文" in request.form:
                        newId = model.insert_cn(form.inputText.data)
                        form.inputId.data = str(newId)
                        flash_info = "录入 \"{}\"，id为{}".format(
                            form.inputText.data, newId)
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
                form_id = int(form.inputId.data)
                id_cn = model.query_cn(form_id)
                
                if id_cn is None:
                    flash_info = "id {} 未找到".format(form_id)
                else:
                    flash_info = "id:{} -> \"{}\"".format(id, id_cn)
                    if "编辑ID" in request.form:
                        if not form.inputText.data:
                            flash_info = "text输入为空"
                        else:
                            result = model.query_id(form.inputText.data)
                            if result[0]:
                                flash_info = "存在 \"{}\"，id为{}".format(form.inputText.data, result[1])
                            else:
                                flash_info = "编辑 {} -> {} -> {}".format(form_id, id_cn, form.inputText.data)
                                model.edit_txt(form_id, Language_pb2.ch, form.inputText.data)
                    elif "删除ID" in request.form:
                        model.delete_lanId(form_id)
                        flash_info = "删除 " + flash_info
                    pass
                pass
            pass
        
        flash(flash_info)

    info = model.query_statistic_info()
    return render_template('hello.html', myform=form, info=info)

@app.route('/query')
def query():
    content = request.args.get('content')
    
    if model.query_id(content) == -1:
        return model.insert_cn(content)

    return model.query_id(content)[1] # return id


@app.route('/edit')
def edit():
    lanId = int(request.args.get('id'))
    content = request.args.get('content')
    lanType = int(request.args.get('lanType'))
    return model.edit_txt(lanId, lanType, content)


@app.route('/history')
def history():
    content = "None"

    if os.path.exists("history.txt"):
        with open("history.txt", "r") as f:
            content = f.read()

    return content


@app.route('/getexcel')
def getexcel():
    excel_path = "Language.xlsx"

    workbook = model.export_workbook()
    workbook.save(excel_path)

    return send_file(excel_path, cache_timeout=-1, as_attachment=True)


@app.route('/getbytes')
def getbytes():
    bytes_path = "language.bytes"
   
    proto_table = model.export_proto_table()

    with open(bytes_path, "wb+") as f:
        f.write(proto_table.SerializeToString())

    return send_file(bytes_path, cache_timeout=-1, as_attachment=True)


flask_port = 5000
LoggerInit.init(level=logging.INFO, filemode='a')

if __name__ == "__main__":
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = 'some_secret'
    app.run(debug=True, host="0.0.0.0", threaded=False, processes=0, port=5000)

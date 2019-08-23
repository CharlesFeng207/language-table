from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from flask import Flask, render_template, flash, request, redirect, url_for, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from time import sleep
import random
import datetime
import os

class Table:
    def __init__(self):
        self.error_txt = None
        self.table_dic = {} # cn -> id
        self.max_id_value = 0

    def load(self, path, shert_name):
        self.path_src = path
        print("loading {}".format(self.path_src))
        try:
            self.workbook_src = load_workbook(self.path_src)
            self.sheet_src = self.workbook_src[shert_name]
            for i in range(5, self.sheet_src.max_row + 1):
                cn_value = self.sheet_src["{}{}".format('B', i)].value
                id_value = self.sheet_src["{}{}".format('A', i)].value
                self.max_id_value = max(self.max_id_value, id_value)
                if cn_value in self.table_dic:
                    self.error_txt = "简体中文 \"{}\" 存在重复！".format(cn_value)
                    break
                self.table_dic[cn_value] = id_value
            print("load complete!")
        except Exception as e:
            self.error_txt = "解析excel表时报错! {}".format(e)
        pass

        print(self.error_txt)

    def insert(self, cn):
        newid = self.max_id_value + 1
        self.table_dic[cn] = newid
        self.max_id_value += 1

        self.workbook_src.save("backup")

        newrow = self.sheet_src.max_row + 1
        self.sheet_src["{}{}".format('B', newrow)].value = cn
        self.sheet_src["{}{}".format('A', newrow)].value = newid
        self.workbook_src.save(self.path_src)

        return newid
        

table = Table()
table.load("Language.xlsx", "Language")

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
                flash_info = "存在 \"{}\"，id为{}".format(form.username.data, table.table_dic[form.username.data])
                copy_text = table.table_dic[form.username.data]
            else:
                copy_text = table.insert(form.username.data)  
                flash_info = "录入 \"{}\"，id为{}".format(form.username.data, table.table_dic[form.username.data])
                 
        flash(flash_info)
        # return redirect(url_for('hello'))
    info = "正在托管{}，当前文本数量: {}".format(table.path_src, len(table.table_dic))
    return render_template('hello.html', form=form, info=info, copy_text=copy_text)

@app.route('/query')
def query():
    content = request.args.get('content')
    if content in table.table_dic:
        return str(table.table_dic[content])
    else:
        return str(table.insert(content))

@app.route('/download')
def download():
   return send_file(table.path_src, cache_timeout=-1, as_attachment=True)

@app.route('/test')
def test():
    # for i in range(0, 50):
    #     table.insert("form.username.data {}".format(table.max_id_value + 1)) 
    return "done"
      

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.secret_key = 'some_secret'
    app.run(debug=True, host ="0.0.0.0", threaded=True, processes=1)
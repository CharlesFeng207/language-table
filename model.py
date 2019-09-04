import pymysql
import datetime
import Language_pb2
from Language_pb2 import LanguageTable, LanguageInfo


def process_sql(func):
    con = pymysql.connect("localhost", "root", "", "language")
    cursor = con.cursor()
    try:
        func(con, cursor)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.close()


def save_history(info):
    with open("history.txt", "a+") as f:
        f.write(
            "{} {}</br>\n".format(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), info))


def query_statistic_info():
    count = 0

    def do(con, cursor):
        nonlocal count
        cursor.execute("select count(*) from language;")
        count = cursor.fetchone()[0]

    process_sql(do)

    return "文本数量: {}".format(count)


def query_id(cn):
    result = -1

    def do(con, cursor):
        nonlocal result
        rows = cursor.execute("select lanId from language where cn=%s", cn)
        if rows > 0:
            result = cursor.fetchone()[0]

    process_sql(do)
    return result


def query_cn(lanId):
    result = None

    def do(con, cursor):
        nonlocal result
        rows = cursor.execute("select cn from language where lanId=%s", lanId)
        if rows > 0:
            result = cursor.fetchone()[0]

    process_sql(do)
    return result


def insert_cn(cn):
    result = -1

    def do(con, cursor):
        nonlocal result
        rows = cursor.execute("INSERT INTO language (cn) VALUES ( %s)", cn)
        if rows > 0:
            result = query_id(cn)

    process_sql(do)

    if result != -1:
        save_history("录入 \"{}\"，id为{}".format(cn, result))

    return result


def get_lanType_name(lanType):
    if lanType == Language_pb2.ch:
        return "cn"
    elif lanType == Language_pb2.en:
        return "en"
    elif lanType == Language_pb2.zh:
        return "zh"
    elif lanType == Language_pb2.jp:
        return "jp"
    elif lanType == Language_pb2.ko:
        return "ko"
    return None


def edit_txt(lanId, lanType, newTxt):
    result = False

    col = get_lanType_name(lanType)

    if result:
        save_history(
            "编辑 {} -> {}, lan:{} ".format(lanId, content, lanType))

    return result


def delete_lanId(lanId):
    result = False

    def do(con, cursor):
        nonlocal result
        rows = cursor.execute("DELETE FROM language WHERE lanId=%s;", lanId)
        if rows > 0:
            result = True

    process_sql(do)

    if result:
        save_history("删除Id {}".format(lanId))

    return result


def export_proto_table():
    #  proto_table = LanguageTable()

    # # id:0 "" "" ""
    # proto_table.infos.append(LanguageInfo())

    # for i in range(table.id_start_row, table.sheet_src.max_row + 1):
    #     info = LanguageInfo()

    #     info.id = table.get_id(i)
    #     for lantype in Language_pb2.LanguageType.values():
    #         s = table.get_lan(i, lantype)
    #         if info.id != 0 and s == "":
    #             s = "[{}没填翻译!] {}".format(info.id, table.get_lan(i, Language_pb2.ch))
    #         info.content.append(s.encode('utf-8'))

    #     proto_table.infos.append(info)
    return None


def export_workbook():
    return None

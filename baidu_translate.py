import http.client
import hashlib
import json
import urllib
import random


def baidu_translate(content, fromLang, toLang):
    appid = '20190903000331676'
    secretKey = 'jA_zfZqgamdgnwsY8k7X'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构

        if "error_code" in js:
            raise Exception(js["error_code"])

        dst=str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst
    except Exception as e:
        print(e)
        return None
    finally:
        if httpClient:
            httpClient.close()

if __name__ == '__main__':
    while True:
        print("请输入要翻译的内容")
        content=input()
        result = baidu_translate(content, "zh", "en")
        print(result)
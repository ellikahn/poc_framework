from bs4 import BeautifulSoup
import hashlib
import re
import json
import operator
import random


# 获取随机整型
def randomInt(num1, num2):
    return str(int(random.randint(num1, num2)))


# 通过contains判断是否再source中存在text
def check_by_contains(source, text):
    return operator.contains(source, text)


# 创建bs对象
def get_bs(filename):
    setting_file = open(filename, 'r', encoding='utf-8').read()
    return BeautifulSoup(setting_file, 'html.parser')


# 在内存中创建变量
def create_variable(key, value):
    globals()[key] = value


# 执行exec并获取返回值
def exec_func(func: str):
    exec_data = {}
    exec(f'ret = {func}', globals(), exec_data)
    return exec_data["ret"]


# 用于从响应体获取正则匹配的数据，并与定义的变量名组成键值对，变量名为键
def get_rematch_var(text, source, var_names: list):  # text正则表达式、source需要匹配的文本、var_names变量名列表
    tmp = {}
    matches = re.findall(text, source)  # 此处可能有bug，自动转义
    for index, match in enumerate(matches):
        tmp[var_names[index]] = match
    return tmp


# 获取source的md5
def get_md5(source):
    hl = hashlib.md5()
    hl.update(source.encode(encoding='utf8'))
    return hl.hexdigest()


# 获取xml中数据
def get_from_xml(file, node):
    bs = get_bs(file)
    text = bs.find(node).text
    return text


# 字典转json
def get_json_str(text):
    return json.dumps(text)





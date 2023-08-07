import requests_html
import yaml
import operator
import hashlib
import re
import random
from bs4 import BeautifulSoup
import importlib


# 解析data字符串
def process_yml_data(text):
    if text is None:
        return None
    tmp = {}
    datas = text.split('&')
    for data in datas:
        tmp[data.split('=')[0]] = data.split('=')[1]
    if tmp == {}:
        return text
    else:
        return tmp


# 创建bs对象
def get_bs(filename):
    setting_file = open(filename, 'r', encoding='utf-8').read()
    return BeautifulSoup(setting_file, 'html.parser')


# 获取xml中数据
def get_from_xml(file, node):
    bs = get_bs(file)
    text = bs.find(node).text
    return text


# 获取requests_html的HTTPsession
def get_session():
    return requests_html.HTMLSession()


# 获取requests_html的resp
def get_response(session, url, method, headers, follow_redirects, data=None, body=None, json=None):
    tmp = None
    if session is None and session != 'None':
        session = requests_html.HTMLSession()
    if data is not None and data != 'None':
        tmp = process_yml_data(data)
    elif body is not None and body != 'None':
        tmp = body.encode('utf-8')
    if json is not None and json != 'None':
        response = session.request(url=url, json=json, method=method, headers=headers,
                                   allow_redirects=follow_redirects)
    else:
        response = session.request(url=url, data=tmp, method=method, headers=headers,
                                   allow_redirects=follow_redirects)
    return response, session


# 获取yml中的字典结构
def analysis_4_YML(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        yml = yaml.safe_load(file)
        return yml


# 通过contains判断是否再source中存在text
def check_by_contains(source, text):
    return operator.contains(source, text)


# 通过bcontains判断是否再source中存在text 待测试
def check_by_bcontains(source, text):
    return operator.contains(source, bytes(text))


def get_md5(source):
    hl = hashlib.md5()
    hl.update(source.encode(encoding='utf8'))
    return hl.hexdigest()


# 为变量source替换sets字典中变量的函数
def use_set(source, sets: dict):
    if isinstance(source, str):
        for key, value in sets.items():
            source = source.replace('{{' + str(key) + '}}', str(value))
        return source
    else:
        return source


# 验证响应的状态码
def checkStatusCode(response, status_code: int):
    return response.status_code == status_code


# 验证响应的指定内容
def checkResp(response, text, source):
    match source:
        case 'response.text':  # body也是这个
            return check_by_contains(response.text, text)
        case 'response.body':  # body也是这个 以防万一
            return check_by_contains(response.text, text)


# 用于从响应体获取正则匹配的数据，并与定义的变量名组成键值对，变量名为键
def get_rematch_var(text, source, var_names: list):  # text正则表达式、source需要匹配的文本、var_names变量名列表
    tmp = {}
    matches = re.findall(text, source)  # 此处可能有bug，自动转义
    for index, match in enumerate(matches):
        tmp[var_names[index]] = match
    return tmp


# 搜索响应 创建output的orders
def search_resp(response, text, source, orders):
    match source:
        case 'response.text':
            return get_rematch_var(text, response.text, orders)
        case 'response.body':
            return get_rematch_var(text, response.text, orders)


# 执行exec并获取返回值 可用于判断yml的expression运算式结果 需要执行请求并将其替换为True or False
def exec_func(func: str):
    exec_data = {}
    exec(f'ret = {func}', globals(), exec_data)
    return exec_data["ret"]


# 处理并执行eval
def eval_func(function_name: str, function_vars: str):
    return eval(f"{function_name}(%s)" % function_vars)


# 在内存中创建变量 eval_func可以通过字符串形式直接找到内存中的变量
def create_variable(key, value):
    globals()[key] = value


# 获取随机整型
def randomInt(num1, num2):
    return str(int(random.randint(num1, num2)))


# 获取随机小写
def randomLowercase(num):
    lis = list('abcdefghijklmnopqrstuvwxyz')
    tmp = ''
    for i in range(num):
        tmp += lis[int(randomInt(0, len(lis) - 1))]
    return tmp


# 往字典添加字典
def add_to_dict(old: dict, new: dict):
    tmp = old
    for n in new:
        tmp[n] = new[n]
    return tmp


# 处理expression得出的结果列表
# [True, False]
def process_resultList(result: list):
    result_str = ''
    for r in result:
        result_str += str(r)
    return str(exec_func(result_str))


# 解析yml的expression
def check_expression(text):
    tmp = text.replace('&&', '&')
    tmp = tmp.replace('||', '|')
    return tmp


# 加载plugins
def load_plugins(module_name):
    return importlib.import_module(f'.{module_name}', 'plugins')


# 调度plugins 参数不是字符串需要使用create_variable方法创建变量，并使用字符串形式的变量名
def use_plugins(function_name, function_vars):
    create_variable('module', load_plugins(function_name))
    return eval_func(f"module.{function_name}", function_vars)


# 解析set
def process_set(poc_datas):
    tmp = {}
    for data in poc_datas['set']:
        if isinstance(poc_datas['set'][data], dict):
            tmp[data] = use_plugins(poc_datas['set'][data]['function'], poc_datas['set'][data]['vars'])
        else:
            tmp[data] = poc_datas['set'][data]
    return tmp


# 解析expression并执行
def process_expression(expression_list, response):
    create_variable('tmp_resp', response)
    new_list = []
    for expression_json in expression_list:
        if expression_json == 'and' or expression_json == 'or':
            new_list.append(f" {expression_json} ")
        else:
            create_variable('tmp_vars', expression_json["vars"])
            new_list.append(use_plugins(expression_json['function'], 'tmp_resp, tmp_vars'))
    return new_list


# 解析output
def process_output(output_list: list, response):
    create_variable('tmp_resp', response)
    new_dict = {}
    for output in output_list:
        create_variable('tmp_orders', output['orders'])
        create_variable('tmp_text', output["vars"])
        new_dict = add_to_dict(new_dict, use_plugins(output['function'], 'tmp_resp, tmp_text, tmp_orders'))
    return new_dict

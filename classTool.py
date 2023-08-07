import tools
import copy
import time


class Poc:

    def __init__(self, filename, url):
        self.filename = filename
        if url[-1:] == "/":
            self.target_url = url[0:-1]
        else:
            self.target_url = url
        self.filedata = tools.analysis_4_YML(filename)
        self.rulse = self.filedata['rules']
        self.session = None  # 一开始为空，需要rule运行后在其返回值中获取，如果返回为空也无所谓，cache决定
        self.sets = {}  # 创建set列表 解析set在poc类中进行
        self.result = {}  # 保存规则运行结果的字典 key为规则名 value为True或False

    def getName(self):
        return self.filedata['name']

    def getExpression(self):
        return tools.check_expression(self.filedata['expression'])

    # 修改运行结果字典
    def __updateResult(self, key, value):
        self.result[key] = value

    # 判断结果 返回True或False
    def __checkResult(self):
        expression = self.getExpression()
        for key, value in self.result.items():
            expression = expression.replace(f"{key}()", str(value))
        return tools.exec_func(expression)

    # 获取Detail
    def getDetail(self):
        author = self.filedata['detail']['author']
        links = self.filedata['detail']['links']
        return f'\t作者：{author}\n\t链接：{links}\n'

    # 创建解析后的sets 主函数中需要先运行它以定义set
    def __create_sets(self):
        try:
            return tools.process_set(self.filedata)
        except KeyError:
            return {}

    # 创建rule对象 并运行其主函数获得结果
    def __RunRules(self):
        rules = copy.deepcopy(self.rulse)
        for rule in rules:
            setattr(self, rule, Rule(self.rulse.pop(rule), self.target_url, self.sets, self.session))
            tmp = getattr(self, rule)
            run = tmp.run()
            if run[2] is not None:
                for order in run[2]:
                    self.sets[order] = run[2][order]
            self.session = run[1]
            self.__updateResult(rule, run[0])

    # 记录日志
    def log4p(self):
        print("存在漏洞，已记录日志")
        with open(f"{tools.get_from_xml('./config.xml', 'logdir')}\\{time.strftime('%Y_%m_%d %H_%M_%S', time.localtime())}logs.txt", 'a', encoding='utf-8') as f:
            f.write(f"url： {self.target_url}\n")
            # f.write(f"检测时间： {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            f.write(f"poc名： {self.getName()}\n")
            f.write(f"参考： \n{self.getDetail()}\n\n")

    # poc运行函数 运行并记录日志
    def run(self):
        self.sets = self.__create_sets()
        self.__RunRules()
        if self.__checkResult():
            self.log4p()
        # print(self.result)
        # print(type(self.__checkResult()))


class Rule:
    # ['path', 'data', 'headers', 'follow_redirects', 'cache', 'method', 'body', 'json']
    __request_list = tools.get_from_xml('config.xml', 'request_param').split(',')

    def __init__(self, datas: dict, url, sets, session=None):
        self.session = session
        self.__url = url
        for data in datas:
            match data:
                case 'request':
                    for param in self.__request_list:
                        try:
                            tmp = tools.use_set(datas[data][param], sets)
                            setattr(self, param, tmp)  # 生成变量
                        except KeyError:
                            continue
                case 'expression_json':
                    new_list = []
                    expressions = datas[data]
                    for expression in expressions:
                        if expression == 'and' or expression == 'or':
                            new_list.append(expression)
                        else:
                            try:
                                expression['vars'] = tools.use_set(expression['vars'], sets)
                                new_list.append(expression)
                            except TypeError or KeyError:
                                new_list.append(expression)
                        pass  # 操作处理expression_json中的字符替换等 在此添加
                    self.expressions = new_list
                case 'output':
                    output_list = []
                    for output in datas[data]:
                        for param in output:
                            if param == 'vars':
                                output[param] = tools.use_set(output[param], sets)
                        output_list.append(output)
                    self.output = output_list

    def getPath(self):
        try:
            return self.path
        except AttributeError:
            return None

    def getCache(self):
        try:
            return self.cache
        except AttributeError:
            return True

    def getData(self):
        try:
            return self.data
        except AttributeError:
            return None

    def getBody(self):
        try:
            return self.body
        except AttributeError:
            return None

    def getJson(self):
        try:
            return self.json
        except AttributeError:
            return None

    def getHeaders(self):
        try:
            return self.headers
        except AttributeError:
            return None

    def get_follow_redirects(self):
        try:
            return self.follow_redirects
        except AttributeError:
            return None

    def getMethod(self):
        try:
            return self.method
        except AttributeError:
            return None

    def getSearch(self):
        try:
            return self.search
        except AttributeError:
            return None

    def getOrders(self):
        try:
            return self.orders
        except AttributeError:
            return None

    def getExpressions(self):
        try:
            return self.expressions
        except AttributeError:
            return None

    def getOutput(self):
        try:
            return self.output
        except AttributeError:
            return None

    # rule主函数 返回poc成功与否的bool、当前的session、output产生的orders
    def run(self):
        headers = self.getHeaders()
        try:
            headers['User-Agent']
        except KeyError:
            headers['User-Agent'] = tools.get_from_xml('./config.xml', 'default-headers')
        except TypeError:
            headers = {'User-Agent': tools.get_from_xml('./config.xml', 'default-headers')}

        # session, url, method, headers, follow_redirects, data
        resp, session = tools.get_response(self.session, self.__url + self.getPath(), self.getMethod(), headers,
                                           self.get_follow_redirects(), self.getData(), self.getBody(), self.getJson())
        result = tools.process_expression(self.getExpressions(), resp)
        if self.getOutput() is not None:
            output = tools.process_output(self.getOutput(), resp)  # 返回output生成的字典
        else:
            output = None

        if self.getCache():
            return [tools.process_resultList(result), session, output]
        else:
            return [tools.process_resultList(result), None, output]


# if __name__ == '__main__':
    # filename = '弹舱/74cms/74cms-sqli-1.yml'
    # test_filename = '弹舱/apache/apache-flink-upload-rce.yml'
    # target_url = 'http://192.168.11.31:8081/'
    # p = Poc(test_filename, target_url)
    # p.run()
    # tools.get_from_xml('./config.xml', 'default-headers')
    # print(time.strftime('%Y_%m_%d %H_%M_%S', time.localtime()))



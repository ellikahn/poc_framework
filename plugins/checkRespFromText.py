import tools


# 从response的text中搜索参数text 返回True或False
def checkRespFromText(response, text):
    return tools.check_by_contains(response.text, text)

# {"function": "checkRespFromText", "vars": "{{r}}"}

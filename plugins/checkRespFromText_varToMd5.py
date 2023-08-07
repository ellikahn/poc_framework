import tools


# 从response的text中搜索参数text 返回True或False
def checkRespFromText_varToMd5(response, text):
    return tools.check_by_contains(response.text, tools.get_md5(text))

# [{"function": "checkRespFromText_varToMd5", "vars": "{{rand}}"}]

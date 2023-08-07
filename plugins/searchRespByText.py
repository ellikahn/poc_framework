import tools


# 通过正则表达式text在response的text中搜索并返回orders字典中需要的值
def searchRespByText(response, text, orders: list):
    return tools.get_rematch_var(text, response.text, orders)
# [{"function": "searchRespByText", "vars": "action=admin&id=(?P<articleid>\\d{1,20})", "orders": ["articleid"]}]

# '"action=admin&id=(?P<articleid>\\d{1,20})".bsubmatch(response.body)'


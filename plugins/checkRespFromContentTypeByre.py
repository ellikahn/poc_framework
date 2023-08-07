import re


def checkRespFromContentTypeByre(response, text):
    if re.search(text, response.headers['Content-Type']):
        return True
    else:
        return False
# {"function": "checkRespFromContentTypeByre", "vars": "json"}

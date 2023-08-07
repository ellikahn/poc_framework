import re


def checkRespFromTextByre(response, text):
    if re.search(text, response.text):
        return True
    else:
        return False
# {"function": "checkRespFromTextByre", "vars": "root:[x*]:0:0:"}

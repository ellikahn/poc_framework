def checkStatusCode(response, status_code):
    return int(response.status_code) == int(status_code)
# [{"function": "checkStatusCode", "vars": 200}]

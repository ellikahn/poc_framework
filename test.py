import json
import requests_html
import tools
import importlib

s = requests_html.HTMLSession()
r = s.get('http://192.168.11.188:8080')
print(r.headers['Content-Type'])


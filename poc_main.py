import classTool


def scan(filename, url):
    p = classTool.Poc(filename, url)
    p.run()

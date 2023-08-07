import tools


def randomLowercase(num):
    lis = list('abcdefghijklmnopqrstuvwxyz')
    tmp = ''
    for i in range(num):
        tmp += lis[int(tools.randomInt(0, len(lis) - 1))]
    return tmp

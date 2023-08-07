import argparse
import os
import poc_main
import tools


projectile_room = tools.get_from_xml('config.xml', 'projectile-room')

parser = argparse.ArgumentParser(description='界面简陋，请多包含')

parser.add_argument('--poc', nargs=1, type=str, help='输入url，后续手动配置poc')

args = parser.parse_args()

if args.poc:
    while True:
        categorylist = os.listdir(projectile_room)
        for file in categorylist:
            print(file)
        category = input("选择分类： (输入quit 退出)\n")
        print()
        if category == 'quit':
            print()
            break
        elif category in categorylist:
            filelist = os.listdir(f'弹舱\\{category}')
            for file in filelist:
                print(file)
            while True:
                filename = input("选择poc： (输入all执行所有poc，输入back返回类别)\n")
                print()
                if filename == 'back':
                    print()
                    break
                if filename == 'all':
                    for file in filelist:
                        poc_main.scan(f'弹舱\\{category}\\{file}', args.poc[0])
                    print(f'{category}类别下poc执行完成')
                elif filename in filelist:
                    poc_main.scan(f'弹舱\\{category}\\{filename}', args.poc[0])
                    print(f"\n{filename}执行成功\n")
                else:
                    print("输入有误\n")
                    continue
        else:
            print("输入有误\n")
            continue



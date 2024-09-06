import os
import sys

def validate_pr_structure():
    # 定义PR中期望的文件结构
    expected_files = [
        'plugin_name.zip',
        'checksum.txt',
        'plugin_name.jpg',  # 或 plugin_name.png
        'plugin_name.json'
    ]
    
    # 从环境变量中获取PR目录或者假设默认路径
    pr_directory = 'plugins'  # PR插件存放目录
    
    # 检查每个期望文件是否存在
    missing_files = []
    for expected_file in expected_files:
        found = False
        # 遍历插件目录，检查是否有指定文件
        for root, dirs, files in os.walk(pr_directory):
            if expected_file in files:
                found = True
                break
        if not found:
            missing_files.append(expected_file)
    
    if missing_files:
        print(f"Error: Missing required files in PR: {', '.join(missing_files)}")
        sys.exit(1)  # 失败
    else:
        print("PR structure validation passed.")
        sys.exit(0)  # 成功

if __name__ == '__main__':
    validate_pr_structure()

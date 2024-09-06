import os
import sys

def validate_pr_structure():
    required_files = ['.zip']  # 只检查是否存在 .zip 文件
    optional_files = ['checksum.txt', '.json']  # 只检查扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    pr_directory = 'plugins'  # 插件提交目录

    missing_files = []
    found_zip = False
    found_image = False
    found_json = False

    for root, dirs, files in os.walk(pr_directory):
        for file in files:
            if file.endswith('.zip'):
                found_zip = True
            elif any(file.endswith(ext) for ext in image_extensions):
                found_image = True
            elif file.endswith('.json'):
                found_json = True
            elif file == 'checksum.txt':
                optional_files.remove('checksum.txt')

    if not found_zip:
        missing_files.append('插件 ZIP 文件')
    if not found_image:
        missing_files.append('插件图片文件 (.jpg/.jpeg/.png/.webp)')
    if not found_json:
        missing_files.append('插件 JSON 文件')

    if missing_files:
        print(f"错误：PR 中缺少以下必需文件：{', '.join(missing_files)}")
        sys.exit(1)
    else:
        print("PR 结构验证通过。")
        sys.exit(0)

if __name__ == '__main__':
    validate_pr_structure()

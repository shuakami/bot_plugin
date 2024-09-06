import os
import sys

def validate_pr_structure():
    required_files = ['plugin_name.zip']
    optional_files = ['checksum.txt', 'plugin_name.json']
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    pr_directory = 'plugins'  # 插件提交目录

    missing_files = []
    found_image = False

    for root, dirs, files in os.walk(pr_directory):
        for file in files:
            if file == 'plugin_name.zip':
                required_files.remove('plugin_name.zip')
            elif any(file.endswith(ext) for ext in image_extensions):
                found_image = True
            elif file in optional_files:
                optional_files.remove(file)

    if 'plugin_name.zip' in required_files:
        missing_files.append('plugin_name.zip')

    if not found_image:
        missing_files.append('plugin_name (image file: .jpg/.jpeg/.png/.webp)')

    if missing_files:
        print(f"错误：PR 中缺少以下必需文件：{', '.join(missing_files)}")
        sys.exit(1)
    else:
        print("PR 结构验证通过。")
        sys.exit(0)

if __name__ == '__main__':
    validate_pr_structure()

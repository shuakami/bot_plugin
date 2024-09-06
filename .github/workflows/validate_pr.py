import os
import sys

def validate_pr_structure():
    # 期望的文件结构（图片文件和 ZIP 文件是必须的）
    required_files = ['plugin_name.zip']
    optional_files = ['checksum.txt', 'plugin_name.json']

    # 允许的图片扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    # 插件提交目录
    pr_directory = 'plugins'  # PR插件存放目录

    # 必须文件和可选文件的检查
    missing_files = []
    found_image = False  # 检查是否有符合条件的图片文件

    for root, dirs, files in os.walk(pr_directory):
        for file in files:
            # 检查 ZIP 文件
            if file.endswith('.zip') and 'plugin_name.zip' in required_files:
                required_files.remove('plugin_name.zip')
            # 检查图片文件
            elif any(file.endswith(ext) for ext in image_extensions):
                found_image = True
            # 检查可选文件
            for opt_file in optional_files:
                if file.endswith(opt_file) and opt_file in optional_files:
                    optional_files.remove(opt_file)

    if 'plugin_name.zip' in required_files:
        missing_files.append('plugin_name.zip')

    if not found_image:
        missing_files.append('plugin_name (image file: .jpg/.jpeg/.png/.webp)')

    if missing_files:
        print(f"Error: Missing required files in PR: {', '.join(missing_files)}")
        sys.exit(1)  # 失败
    else:
        print("PR structure validation passed.")
        sys.exit(0)  # 成功

if __name__ == '__main__':
    validate_pr_structure()

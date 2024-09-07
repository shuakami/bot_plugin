import os
import sys
import hashlib

def generate_checksum(file_path):
    """生成文件的 SHA-256 校验和"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 分块读取文件，避免大文件导致内存占用过高
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def validate_pr_structure():
    required_files = ['.zip']  # 检查是否存在 .zip 文件
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
                zip_file_path = os.path.join(root, file)
                checksum_file_path = os.path.join(root, 'checksum.txt')

                # 检查 checksum.txt 是否存在且非空，否则生成新的 checksum.txt
                if not os.path.exists(checksum_file_path) or os.path.getsize(checksum_file_path) == 0:
                    print(f"正在为 {file} 生成 checksum.txt 文件...")
                    checksum_value = generate_checksum(zip_file_path)
                    with open(checksum_file_path, 'w') as checksum_file:
                        checksum_file.write(checksum_value)
                    print(f"{file} 的 checksum.txt 已生成，内容为：{checksum_value}")

            elif any(file.endswith(ext) for ext in image_extensions):
                found_image = True
            elif file.endswith('.json'):
                found_json = True

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

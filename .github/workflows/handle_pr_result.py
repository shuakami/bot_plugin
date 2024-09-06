import os
import requests
from github import Github
import time

# VirusTotal API 密钥
VIRUSTOTAL_API_KEY = '65ec907912bd4e75751d820c3957aef618a01e7ac996cf58953985c254395355'

def comment_on_pr(repo, pr_number, message):
    """在 PR 上添加评论"""
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)
    print(f"已在 PR #{pr_number} 上评论：{message}")

def scan_file_with_virustotal(file_path):
    """使用 VirusTotal API 对文件进行扫描"""
    print(f"开始使用 VirusTotal 扫描 {file_path}...")

    # 上传文件至 VirusTotal
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {
        'x-apikey': VIRUSTOTAL_API_KEY
    }
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
    
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()  # 检查请求是否成功
    except requests.exceptions.RequestException as e:
        print(f"文件上传失败：{e}")
        return False, None

    # 获取文件扫描 ID
    scan_id = response.json().get('data', {}).get('id')
    if not scan_id:
        print("无法获取扫描 ID。")
        return False, None

    print(f"文件 {file_path} 上传成功，扫描 ID: {scan_id}")

    # 查询扫描结果
    result_url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
    while True:
        try:
            result_response = requests.get(result_url, headers=headers)
            result_response.raise_for_status()
            result_data = result_response.json()
            
            status = result_data.get('data', {}).get('attributes', {}).get('status')
            if status == 'completed':
                print(f"文件 {file_path} 的扫描完成。")
                stats = result_data['data']['attributes']['stats']
                return True, stats
            elif status == 'queued':
                print(f"文件 {file_path} 的扫描在队列中，等待中...")
                time.sleep(10)
            else:
                print(f"未知状态：{status}")
                return False, None
        except requests.exceptions.RequestException as e:
            print(f"获取扫描结果失败：{e}")
            return False, None

def handle_pr_result():
    """处理 PR 的结果，执行病毒扫描"""
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    REPO_NAME = os.getenv('GITHUB_REPOSITORY')

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    open_prs = repo.get_pulls(state='open')
    if open_prs.totalCount == 0:
        print("没有打开的 PR, 结束脚本。")
        return

    for pr in open_prs:
        pr_number = pr.number
        pr_title = pr.title
        print(f"开始处理 PR #{pr_number}：{pr_title}")

        # 获取 PR 中的所有 zip 文件
        zip_files = []
        for root, dirs, files in os.walk("plugins"):
            for file in files:
                if file.endswith(".zip"):
                    zip_files.append(os.path.join(root, file))

        # 执行病毒扫描
        all_scans_passed = True
        for zip_file in zip_files:
            scan_passed, stats = scan_file_with_virustotal(zip_file)

            if scan_passed:
                # 如果扫描成功，检查是否有检测到病毒
                if stats['malicious'] > 0:
                    all_scans_passed = False
                    message = f"文件 {zip_file} 的 VirusTotal 扫描发现 {stats['malicious']} 个恶意检测。\n"
                    comment_on_pr(repo, pr_number, message)
                else:
                    message = f"文件 {zip_file} 的 VirusTotal 扫描通过，无恶意软件。\n"
                    comment_on_pr(repo, pr_number, message)
            else:
                all_scans_passed = False
                message = f"文件 {zip_file} 的 VirusTotal 扫描失败。"
                comment_on_pr(repo, pr_number, message)

        # 最终结果输出
        if all_scans_passed:
            comment_on_pr(repo, pr_number, "所有文件的病毒扫描通过，无病毒。")
        else:
            comment_on_pr(repo, pr_number, "病毒扫描检测到恶意软件，请查看上面的详细结果。")

if __name__ == '__main__':
    handle_pr_result()

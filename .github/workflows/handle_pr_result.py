import os
import requests
from github import Github

def comment_on_pr(repo, pr_number, message):
    """在 PR 上添加评论"""
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)
    print(f"已在 PR #{pr_number} 上评论：{message}")

def run_virus_scan(zip_files):
    """使用 VirusTotal 对给定的 zip 文件列表进行病毒扫描"""
    api_key = '65ec907912bd4e75751d820c3957aef618a01e7ac996cf58953985c254395355'
    virus_total_url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    headers = {"x-apikey": api_key}
    scan_results = {}

    for zip_file in zip_files:
        print(f"开始使用 VirusTotal 扫描 {zip_file}...")

        # 上传文件进行扫描
        with open(zip_file, 'rb') as file:
            files = {'file': (os.path.basename(zip_file), file)}
            response = requests.post(virus_total_url, files=files, headers=headers)
        
        if response.status_code == 200:
            scan_id = response.json().get('scan_id')
            scan_results[zip_file] = scan_id
            print(f"{zip_file} 上传成功，扫描 ID: {scan_id}")
        else:
            print(f"上传 {zip_file} 失败，状态码：{response.status_code}，响应：{response.text}")
            return False, None

    # 等待并获取扫描结果
    report_url = 'https://www.virustotal.com/vtapi/v2/file/report'
    for zip_file, scan_id in scan_results.items():
        params = {'apikey': api_key, 'resource': scan_id}
        response = requests.get(report_url, params=params)

        if response.status_code == 200:
            scan_data = response.json()
            if scan_data['positives'] > 0:
                print(f"VirusTotal 扫描发现 {zip_file} 中存在病毒或恶意软件。")
                return False, scan_data
            else:
                print(f"{zip_file} 扫描通过，无病毒。")
        else:
            print(f"获取 {zip_file} 的扫描结果失败，状态码：{response.status_code}，响应：{response.text}")
            return False, None

    return True, None

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
        scan_passed, scan_data = run_virus_scan(zip_files)

        # 将扫描结果发送至 PR 评论
        if scan_passed:
            comment_on_pr(repo, pr_number, "插件病毒扫描通过，无病毒。")
        else:
            if scan_data:
                log_content = f"发现病毒或恶意软件：\n\n{scan_data}"
            else:
                log_content = "病毒扫描失败，无法获取详细信息。"
            comment_on_pr(repo, pr_number, f"插件病毒扫描失败。以下是日志：\n\n```\n{log_content}\n```")

if __name__ == '__main__':
    handle_pr_result()

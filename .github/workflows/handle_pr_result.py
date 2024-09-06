import os
import subprocess
from github import Github

def comment_on_pr(repo, pr_number, message):
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)
    print(f"已在 PR #{pr_number} 上评论：{message}")

def merge_pr_if_passed(repo, pr_number):
    pr = repo.get_pull(pr_number)
    pr.merge(merge_method='squash')
    print(f"PR #{pr_number} 已成功合并。")

def close_pr(repo, pr_number):
    pr = repo.get_pull(pr_number)
    pr.edit(state='closed')
    print(f"PR #{pr_number} 已关闭。")

def run_virus_scan(zip_files):
    log_filename = "virus_scan.log"

    # 更新 ClamAV 病毒数据库
    print("正在更新 ClamAV 病毒数据库...")
    subprocess.run(["freshclam"])

    # 使用 ClamAV 扫描所有 zip 文件
    with open(log_filename, "w") as log_file:
        for zip_file in zip_files:
            print(f"开始使用 ClamAV 扫描 {zip_file}...")
            clamav_result = subprocess.run(["clamscan", "--archive-verbose", zip_file], stdout=log_file, stderr=subprocess.STDOUT)
            if clamav_result.returncode != 0:
                print(f"ClamAV 扫描发现 {zip_file} 中存在病毒或威胁。请查看日志。")
                return False, log_filename

    return True, log_filename

def handle_pr_result():
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    REPO_NAME = os.getenv('GITHUB_REPOSITORY')

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    open_prs = repo.get_pulls(state='open')
    if open_prs.totalCount == 0:
        print("没有打开的 PR,结束脚本。")
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
        scan_passed, log_filename = run_virus_scan(zip_files)

        if scan_passed:
            comment_on_pr(repo, pr_number, "插件病毒扫描通过,正在合并 PR...")
            merge_pr_if_passed(repo, pr_number)
        else:
            with open(log_filename, "r") as log_file:
                log_content = log_file.read()
            comment_on_pr(repo, pr_number, f"插件病毒扫描失败。以下是日志：\n\n```\n{log_content}\n```")
            close_pr(repo, pr_number)

if __name__ == '__main__':
    handle_pr_result()

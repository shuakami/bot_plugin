import os
import subprocess  # nosec
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

def run_security_checks():
    log_filename = "security_scan.log"

    # 运行 bandit 检查代码漏洞
    with open(log_filename, "w") as log_file:
        print("开始运行 Bandit 检查...")
        bandit_result = subprocess.run(["bandit", "-r", "."], stdout=log_file, stderr=subprocess.STDOUT)  # nosec
        if bandit_result.returncode != 0:
            print("Bandit 检查发现问题。请查看日志。")
            return False, log_filename

    # 运行 safety 检查依赖项漏洞
    with open(log_filename, "a") as log_file:
        print("开始运行 Safety 检查...")
        safety_result = subprocess.run(["safety", "check"], stdout=log_file, stderr=subprocess.STDOUT)  # nosec
        if safety_result.returncode != 0:
            print("Safety 检查发现问题。请查看日志。")
            return False, log_filename

    return True, log_filename

def handle_pr_result():
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    REPO_NAME = os.getenv('GITHUB_REPOSITORY')

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    open_prs = repo.get_pulls(state='open')
    if open_prs.totalCount == 0:
        print("没有打开的 PR，结束脚本。")
        return

    for pr in open_prs:
        pr_number = pr.number
        pr_title = pr.title
        print(f"开始处理 PR #{pr_number}：{pr_title}")

        # 执行安全检查
        validation_passed, log_filename = run_security_checks()

        if validation_passed:
            comment_on_pr(repo, pr_number, "插件安全检查通过，正在合并 PR...")
            merge_pr_if_passed(repo, pr_number)
        else:
            with open(log_filename, "r") as log_file:
                log_content = log_file.read()
            comment_on_pr(repo, pr_number, f"插件安全检查失败。以下是日志：\n\n```\n{log_content}\n```")
            close_pr(repo, pr_number)

if __name__ == '__main__':
    handle_pr_result()

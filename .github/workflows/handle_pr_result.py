import os
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

        # 模拟安全检查
        validation_passed = perform_security_checks(pr_number)

        if validation_passed:
            comment_on_pr(repo, pr_number, "插件安全检查通过，正在合并 PR...")
            merge_pr_if_passed(repo, pr_number)
        else:
            comment_on_pr(repo, pr_number, "插件安全检查失败，PR 将被关闭。")
            close_pr(repo, pr_number)

def perform_security_checks(pr_number):
    # 这里应该执行真正的安全检查逻辑，可以替换为你自己的安全检查工具。
    print(f"对 PR #{pr_number} 进行安全检查...")
    # 模拟检查通过
    return True

if __name__ == '__main__':
    handle_pr_result()

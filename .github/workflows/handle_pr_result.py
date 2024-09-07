import os
from github import Github
import time

def comment_on_pr(repo, pr_number, message):
    """在 PR 上添加评论"""
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)
    print(f"已在 PR #{pr_number} 上评论：{message}")

def merge_pr(repo, pr_number):
    """尝试合并 PR 并删除分支"""
    pr = repo.get_pull(pr_number)
    if pr.mergeable_state == 'clean':
        try:
            pr.merge()
            print(f"PR #{pr_number} 已合并。")

            # 删除分支
            ref = f"heads/{pr.head.ref}"
            repo.get_git_ref(ref).delete()
            print(f"已删除 PR #{pr_number} 的分支：{ref}")
        except Exception as e:
            print(f"合并 PR #{pr_number} 失败：{e}")
    else:
        print(f"PR #{pr_number} 无法自动合并。状态：{pr.mergeable_state}")
        # 尝试三次强制合并
        attempt_count = 0
        while attempt_count < 3:
            try:
                pr.merge(merge_method='merge')
                print(f"PR #{pr_number} 已强制合并。")
                # 删除分支
                ref = f"heads/{pr.head.ref}"
                repo.get_git_ref(ref).delete()
                print(f"已删除 PR #{pr_number} 的分支：{ref}")
                return
            except Exception as e:
                attempt_count += 1
                print(f"强制合并 PR #{pr_number} 失败：{e}，重试 {attempt_count} 次")
                time.sleep(2)  # 等待 2 秒后重试

        print(f"强制合并 PR #{pr_number} 失败，尝试 3 次后仍无法合并。")

def close_pr(repo, pr_number):
    """关闭 PR 并删除分支"""
    pr = repo.get_pull(pr_number)
    pr.edit(state='closed')
    print(f"PR #{pr_number} 已关闭。")

    # 删除分支
    ref = f"heads/{pr.head.ref}"
    try:
        repo.get_git_ref(ref).delete()
        print(f"已删除 PR #{pr_number} 的分支：{ref}")
    except Exception as e:
        print(f"删除分支失败：{e}")

def handle_pr_result():
    """处理 ClamAV 扫描结果并在 PR 上发表评论"""
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    REPO_NAME = os.getenv('GITHUB_REPOSITORY')

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    open_prs = repo.get_pulls(state='open')
    if open_prs.totalCount == 0:
        print("没有打开的 PR, 结束脚本。")
        return

    all_scans_passed = True
    scan_results_file = "scan_results/clamav_scan_summary.txt"

    if not os.path.exists(scan_results_file):
        print("没有找到扫描结果文件。")
        return

    with open(scan_results_file, 'r') as f:
        scan_output = f.read()
        if "FOUND" in scan_output:
            all_scans_passed = False
            message = f"ClamAV 扫描发现以下文件中存在恶意软件：\n\n{scan_output}"
        else:
            message = "所有文件的 ClamAV 病毒扫描通过，无病毒。"

    # 根据扫描结果处理每个打开的 PR
    for pr in open_prs:
        pr_number = pr.number
        print(f"开始处理 PR #{pr_number}")
        comment_on_pr(repo, pr_number, message)

        if all_scans_passed:
            merge_pr(repo, pr_number)
        else:
            close_pr(repo, pr_number)

if __name__ == '__main__':
    handle_pr_result()

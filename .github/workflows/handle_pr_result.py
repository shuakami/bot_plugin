import os
import requests
from github import Github

def comment_on_pr(repo, pr_number, message):
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)

def merge_pr_if_passed(repo, pr_number):
    pr = repo.get_pull(pr_number)
    pr.merge(merge_method='squash')
    print(f"PR #{pr_number} merged successfully.")

def handle_pr_result():
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    REPO_NAME = os.getenv('GITHUB_REPOSITORY')
    PR_NUMBER = os.getenv('GITHUB_EVENT_NUMBER')  # This will get the PR number

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # This assumes a file was created by the previous steps indicating if the PR passed validation
    result_file = ".github/workflows/pr_validation_result.txt"
    
    if not os.path.exists(result_file):
        comment_on_pr(repo, PR_NUMBER, "PR validation failed due to missing result file.")
        exit(1)
    
    with open(result_file, "r") as f:
        result = f.read().strip()
    
    if result == "success":
        comment_on_pr(repo, PR_NUMBER, "PR validation passed. Merging PR...")
        merge_pr_if_passed(repo, PR_NUMBER)
    else:
        comment_on_pr(repo, PR_NUMBER, f"PR validation failed: {result}")

if __name__ == '__main__':
    handle_pr_result()

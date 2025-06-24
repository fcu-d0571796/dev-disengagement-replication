import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========
GITHUB_TOKEN = "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"  # <<< 你的 GitHub Token
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
REPO_LIST_FILE = "repo_list.txt"  # 包含 60 个项目的文本文件，每行一个 full_name
SAVE_DIR = Path("data_v2")
SAVE_DIR.mkdir(exist_ok=True)

DATE_START = pd.Timestamp("2024-02-01T00:00:00Z")
DATE_END = pd.Timestamp("2025-05-01T00:00:00Z")
MAX_COMMENTS_PER_REPO = 1000
# ===========================

def load_repo_list(file_path):
    with open(file_path, "r") as f:
        repos = [line.strip() for line in f if line.strip()]
    return repos[:10]  # 只取前10个项目

def get_issues(repo):
    """ 获取所有符合条件的 issue：state=all, comments>1 """
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {"state": "all", "sort": "comments", "direction": "desc", "per_page": 100, "page": page}
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200:
            print(f"❌ 无法获取 issue 列表: HTTP {r.status_code} for {repo}")
            break
        batch = r.json()
        if not batch:
            break
        for issue in batch:
            if "pull_request" in issue:
                continue  # 排除 PR
            if issue["comments"] < 2:
                continue
            created_at = pd.to_datetime(issue["created_at"])
            if not (DATE_START <= created_at <= DATE_END):
                continue
            issues.append(issue)
        if len(issues) >= 300:
            break
        page += 1
        time.sleep(0.5)
    return issues[:300]

def get_issue_comments(repo, issue_number):
    comments = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        params = {"per_page": 100, "page": page}
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        for c in batch:
            if not c.get("user") or "bot" in c["user"]["login"].lower():
                continue
            if len(c.get("body", "").strip()) < 10:
                continue
            created_at = pd.to_datetime(c["created_at"])
            if not (DATE_START <= created_at <= DATE_END):
                continue
            comments.append({
                "repo": repo,
                "issue_number": issue_number,
                "comment_id": c["id"],
                "commenter": c["user"]["login"],
                "created_at": created_at.isoformat(),
                "body": c["body"].strip()
            })
        page += 1
        time.sleep(0.3)
    return comments

def fetch_project(repo):
    print(f"🔍 抓取项目: {repo}")
    all_comments = []
    threads = []
    try:
        issues = get_issues(repo)
        valid_comment_count = 0
        for issue in issues:
            number = issue["number"]
            comments = get_issue_comments(repo, number)
            if not comments:
                continue
            all_comments.extend(comments)
            created_times = [pd.to_datetime(c["created_at"]) for c in comments]
            participants = {c["commenter"] for c in comments}
            threads.append({
                "repo": repo,
                "issue_number": number,
                "thread_start": min(created_times).isoformat(),
                "thread_end": max(created_times).isoformat(),
                "num_comments": len(comments),
                "num_participants": len(participants)
            })
            valid_comment_count += len(comments)
            if valid_comment_count >= MAX_COMMENTS_PER_REPO:
                break
    except Exception as e:
        print(f"⚠️ 错误 {repo}: {e}")
    print(f"✅ 有效评论数: {len(all_comments)}")
    return all_comments, threads

def main():
    repos = load_repo_list(REPO_LIST_FILE)
    all_comments = []
    all_threads = []

    for repo in repos:
        comments, threads = fetch_project(repo)
        all_comments.extend(comments)
        all_threads.extend(threads)

    # 保存合并结果
    pd.DataFrame(all_comments).to_csv(SAVE_DIR / "comments_batch4.csv", index=False)
    pd.DataFrame(all_threads).to_csv(SAVE_DIR / "threads_batch4.csv", index=False)

    print(f"✅ 共抓取评论数: {len(all_comments)}")
    print(f"✅ 共构造 thread 数: {len(all_threads)}")

if __name__ == "__main__":
    main()
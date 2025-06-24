import requests
import pandas as pd
from collections import defaultdict
from datetime import datetime
import itertools
import time

# === 配置 ===
DATE_START = pd.Timestamp("2024-02-01T00:00:00Z")
DATE_END = pd.Timestamp("2025-05-01T00:00:00Z")

def load_repo_list(file_path):
    with open(file_path, "r") as f:
        repos = [line.strip() for line in f if "/" in line.strip()]
    return repos[:5]  # 只取前两个项目，可调整

with open("tokens.txt") as f:
    TOKENS = [line.strip() for line in f if line.strip()]

REPOS = load_repo_list("repo_list.txt")
TOKEN_CYCLE = itertools.cycle(TOKENS)

def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def month_key(date_str):
    return pd.to_datetime(date_str).strftime("%Y-%m")

def fetch_commit_data(repos):
    rows = []
    anonymous_skipped = 0
    bot_skipped = 0

    for repo in repos:
        owner, name = repo.split("/")
        print(f"🔍 Fetching commits for repo: {repo}")
        data = defaultdict(lambda: defaultdict(lambda: {"commit_count": 0, "churn_add": 0, "churn_del": 0}))
        page = 1

        while True:
            token = next(TOKEN_CYCLE)
            url = f"https://api.github.com/repos/{owner}/{name}/commits"
            params = {
                "since": DATE_START.isoformat(),
                "until": DATE_END.isoformat(),
                "per_page": 100,
                "page": page
            }
            headers = get_headers(token)
            resp = requests.get(url, headers=headers, params=params)

            if resp.status_code == 403:  # Rate limit
                reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait_time = max(1, reset_time - time.time())
                print(f"⏳ Rate limited, sleeping {int(wait_time)}s...")
                time.sleep(wait_time)
                continue  # use next token on retry
            elif resp.status_code != 200:
                print(f"❌ Error {resp.status_code}: {resp.text}")
                break

            commits = resp.json()
            if not commits:
                break

            for commit in commits:
                try:
                    if not commit.get("author") or not commit["author"].get("login"):
                        anonymous_skipped += 1
                        continue

                    author = commit["author"]["login"]
                    if "bot" in author.lower():
                        bot_skipped += 1
                        continue

                    date = commit["commit"]["author"]["date"]
                    month = month_key(date)
                    sha = commit["sha"]

                    # Fetch detailed commit info for churn stats
                    commit_url = f"https://api.github.com/repos/{owner}/{name}/commits/{sha}"
                    commit_resp = requests.get(commit_url, headers=headers)
                    if commit_resp.status_code != 200:
                        continue

                    commit_data = commit_resp.json()
                    additions = commit_data.get("stats", {}).get("additions", 0)
                    deletions = commit_data.get("stats", {}).get("deletions", 0)

                    d = data[author][month]
                    d["commit_count"] += 1
                    d["churn_add"] += additions
                    d["churn_del"] += deletions

                except Exception as e:
                    print(f"⚠️ Error processing commit: {e}")
                    continue

            if len(commits) < 100:
                break
            else:
                page += 1
                time.sleep(1)

        # 保存为行
        for commenter, months in data.items():
            for month, stats in months.items():
                rows.append({
                    "repo": repo,
                    "commenter": commenter,
                    "month": month,
                    "commit_count": stats["commit_count"],
                    "churn_add": stats["churn_add"],
                    "churn_del": stats["churn_del"],
                })

    print(f"✅ Finished. Skipped {anonymous_skipped} anonymous and {bot_skipped} bot commits.")
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = fetch_commit_data(REPOS)
    df.to_csv("commits_summary_batch5.csv", index=False)
    print("📁 Saved to commits_summary.csv")
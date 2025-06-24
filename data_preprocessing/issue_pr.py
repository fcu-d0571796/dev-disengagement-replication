import requests, pandas as pd, time, itertools
from datetime import datetime
from pathlib import Path

# === 时间范围 ===
DATE_START = pd.Timestamp("2024-02-01T00:00:00Z")
DATE_END   = pd.Timestamp("2025-05-01T00:00:00Z")

# === 加载 repo 和 token ===
def load_repo_list(file_path):
    with open(file_path, "r") as f:
        repos = [line.strip() for line in f if "/" in line.strip()]
    return repos[:10]  # 可改为所需数量

with open("tokens.txt") as f:
    TOKENS = [line.strip() for line in f if line.strip()]
REPOS = load_repo_list("repo_list.txt")

GRAPHQL_QUERY = Path("github_graphql_query.graphql").read_text()
GITHUB_API_URL = "https://api.github.com/graphql"
token_pool = itertools.cycle(TOKENS)

def run_query(owner, name, token):
    headers = {"Authorization": f"bearer {token}"}
    variables = {"owner": owner, "name": name, "cursor": None}
    all_issues, all_prs = [], []

    # === Issues ===
    variables["cursor"] = None
    while True:
        r = requests.post(GITHUB_API_URL, json={"query": GRAPHQL_QUERY, "variables": variables}, headers=headers)
        if r.status_code != 200:
            print(f"Issue request failed: {r.status_code}, {r.text}")
            break
        data = r.json()["data"]["repository"]
        issues = data["issues"]
        for node in issues["nodes"]:
            login = node["author"]["login"] if node["author"] else None
            if login and "bot" not in login.lower() and node["createdAt"] and node["closedAt"]:
                created_at = pd.Timestamp(node["createdAt"])
                closed_at = pd.Timestamp(node["closedAt"])
                if DATE_START <= created_at <= DATE_END:
                    delta_hr = (closed_at - created_at).total_seconds() / 3600
                    all_issues.append({
                        "repo": f"{owner}/{name}",
                        "commenter": login,
                        "created_at": created_at,
                        "closed_at": closed_at,
                        "bug_fix_time_hrs": delta_hr
                    })
        if not issues["pageInfo"]["hasNextPage"]:
            break
        variables["cursor"] = issues["pageInfo"]["endCursor"]

    # === PRs ===
    variables["cursor"] = None
    while True:
        r = requests.post(GITHUB_API_URL, json={"query": GRAPHQL_QUERY, "variables": variables}, headers=headers)
        if r.status_code != 200:
            print(f"PR request failed: {r.status_code}, {r.text}")
            break
        data = r.json()["data"]["repository"]
        prs = data["pullRequests"]
        for node in prs["nodes"]:
            login = node["author"]["login"] if node["author"] else None
            created = node.get("createdAt")
            merged = node.get("mergedAt")
            if login and "bot" not in login.lower() and created:
                created_at = pd.Timestamp(created)
                if DATE_START <= created_at <= DATE_END:
                    all_prs.append({
                        "repo": f"{owner}/{name}",
                        "commenter": login,
                        "created_at": created_at,
                        "merged_at": pd.Timestamp(merged) if merged else None,
                        "merged": 1 if merged else 0
                    })
        if not prs["pageInfo"]["hasNextPage"]:
            break
        variables["cursor"] = prs["pageInfo"]["endCursor"]

    return all_issues, all_prs

# === 抓取数据 ===
issues_all, prs_all = [], []

for repo in REPOS:
    owner, name = repo.split("/")
    token = next(token_pool)
    print(f"Fetching {owner}/{name}")
    try:
        issues, prs = run_query(owner, name, token)
        issues_all.extend(issues)
        prs_all.extend(prs)
    except Exception as e:
        print(f"❌ Error in {repo}: {e}")
    time.sleep(1)

# === 保存为 CSV ===
pd.DataFrame(issues_all).to_csv("issues_raw_batch5.csv", index=False)
pd.DataFrame(prs_all).to_csv("prs_raw_batch5.csv", index=False)
print("✅ 抓取完成，已保存为：issues_raw.csv / prs_raw.csv")
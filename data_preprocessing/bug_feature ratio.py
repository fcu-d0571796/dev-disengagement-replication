import requests
import time
from datetime import datetime
import csv

# 读token列表，轮换使用
def load_tokens(path='token.txt'):
    with open(path, 'r') as f:
        tokens = [line.strip() for line in f if line.strip()]
    return tokens

# 轮换token管理器
class TokenRotator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def get_token(self):
        token = self.tokens[self.index]
        self.index = (self.index + 1) % len(self.tokens)
        return token

# 读repo列表
def load_repos(path='repo_list.txt', n=5):
    with open(path, 'r') as f:
        repos = [line.strip() for line in f if line.strip()]
    return repos[:n]

START_DATE = '2024-02-01T00:00:00Z'
END_DATE = '2025-05-01T00:00:00Z'

def is_issue(issue):
    return 'pull_request' not in issue

def has_label(issue, keywords):
    labels = [label['name'].lower() for label in issue.get('labels', [])]
    return any(k.lower() in labels for k in keywords)

def fetch_issues(owner_repo, token_rotator):
    bug_count = 0
    feature_count = 0
    total_count = 0
    page = 1
    per_page = 100

    while True:
        token = token_rotator.get_token()
        headers = {'Authorization': f'token {token}'}
        url = f'https://api.github.com/repos/{owner_repo}/issues'
        params = {
            'state': 'all',
            'since': START_DATE,
            'per_page': per_page,
            'page': page
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 403:
            print(f"Rate limit hit for token, switching token and waiting...")
            time.sleep(2)
            continue
        if response.status_code != 200:
            print(f"Error fetching {owner_repo} page {page}: {response.status_code}")
            break

        issues = response.json()
        if not issues:
            break

        for issue in issues:
            if not is_issue(issue):
                continue

            created_at = issue.get('created_at')
            if created_at is None:
                continue
            created_time = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
            if created_time > datetime.strptime(END_DATE, '%Y-%m-%dT%H:%M:%SZ'):
                return bug_count, feature_count, total_count

            total_count += 1
            if has_label(issue, ['bug']):
                bug_count += 1
            if has_label(issue, ['feature', 'enhancement']):
                feature_count += 1

        page += 1
        time.sleep(1)  # 避免请求太快被限流

    return bug_count, feature_count, total_count

def main():
    tokens = load_tokens()
    token_rotator = TokenRotator(tokens)
    repos = load_repos()

    results = []
    for repo in repos:
        print(f"Processing {repo} ...")
        bug, feature, total = fetch_issues(repo, token_rotator)
        print(f"{repo} - Total: {total}, Bug: {bug}, Feature: {feature}")
        results.append([repo, total, bug, feature])

    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'total_issues', 'bug_issues', 'feature_issues'])
        writer.writerows(results)

if __name__ == '__main__':
    main()

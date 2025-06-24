import pandas as pd

# 读取原始数据
df = pd.read_csv("issues_merged.csv")
print(f"原始记录数: {len(df)}")

# 时间格式转换
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")

# 清除缺失时间
df = df.dropna(subset=["created_at", "closed_at"])
print(f"去除时间缺失后: {len(df)}")

# 去除 bug_fix_time 异常值
df = df[df["bug_fix_time_hrs"] > 0]
df = df[df["bug_fix_time_hrs"] < 8760]
print(f"去除 bug_fix_time 异常值后: {len(df)}")

# 去除重复记录
df = df.drop_duplicates()
print(f"最终记录数（去重后）: {len(df)}")

# 保存清洗后文件
df.to_csv("issues_cleaned.csv", index=False)


import pandas as pd

# 读取原始数据
df = pd.read_csv("prs_merged.csv")
print(f"原始记录数: {len(df)}")

# 保留已合并的 PR
df = df[df["merged"] == True]
print(f"保留 merged=True 后: {len(df)}")

# 转换时间格式
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["merged_at"] = pd.to_datetime(df["merged_at"], errors="coerce")

# 去除时间缺失项
df = df.dropna(subset=["created_at", "merged_at"])
print(f"去除时间缺失后: {len(df)}")

# 去除明显的 bot 用户
bot_pattern = r'(\[bot\]$|-bot$)'
df = df[~df["commenter"].str.lower().str.contains(bot_pattern, regex=True)]
print(f"去除 bot 用户后: {len(df)}")

# 去除重复记录（如果有）
df = df.drop_duplicates()
print(f"最终记录数（去重后）: {len(df)}")

# 保存清洗结果
df.to_csv("prs_cleaned.csv", index=False)



import pandas as pd

# 读取原始数据
df = pd.read_csv("commits_summary_all.csv")
print(f"原始记录数: {len(df)}")

# 去除 bot 用户
bot_pattern = r'(\[bot\]$|-bot$)'
df = df[~df["commenter"].str.lower().str.contains(bot_pattern, regex=True)]
print(f"去除 bot 用户后: {len(df)}")

# 去除 commit_count 为 0 的记录
df = df[df["commit_count"] > 0]
print(f"去除 commit_count 为 0 后: {len(df)}")

# 去除 churn 为负值的记录
df = df[(df["churn_add"] >= 0) & (df["churn_del"] >= 0)]
print(f"去除 churn 为负值后: {len(df)}")

# 去除重复记录
df = df.drop_duplicates()
print(f"最终记录数（去重后）: {len(df)}")

# 可选：去除提交总数过低的开发者（例如总数 < 3）
committer_commit_counts = df.groupby("commenter")["commit_count"].sum()
low_activity_committers = committer_commit_counts[committer_commit_counts < 3].index
df = df[~df["commenter"].isin(low_activity_committers)]
print(f"去除低活跃开发者后: {len(df)}")

# 保存清洗结果
df.to_csv("commits_cleaned.csv", index=False)


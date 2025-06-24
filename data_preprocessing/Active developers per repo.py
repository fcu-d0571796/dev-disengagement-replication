import pandas as pd

# 读取 CSV 文件
df = pd.read_csv('user_activity_metrics_with_repo.csv')

# 按 repo 分组，统计每个 repo 中独特 commenter 的数量（活跃开发者数量）
active_dev_counts = df.groupby('repo')['commenter'].nunique()

# 找出最小和最大活跃人数及对应 repo
min_devs = active_dev_counts.min()
max_devs = active_dev_counts.max()
min_repo = active_dev_counts.idxmin()
max_repo = active_dev_counts.idxmax()

print(f"最少活跃开发者：{min_devs}（项目：{min_repo}）")
print(f"最多活跃开发者：{max_devs}（项目：{max_repo}）")


import pandas as pd

# 加载数据
df = pd.read_csv('comments_all.csv')

# 假设项目名称字段是 'repo'，评论 ID 是 'comment_id'
# 如果你的列名不一样，请根据实际调整
comments_per_project = df.groupby('repo')['comment_id'].count().reset_index()
comments_per_project.columns = ['repo', 'comment_count']

# 输出基本统计
print("Min:", comments_per_project['comment_count'].min())
print("Max:", comments_per_project['comment_count'].max())
print("Mean:", comments_per_project['comment_count'].mean())
print("Median:", comments_per_project['comment_count'].median())

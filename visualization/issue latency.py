import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 加载数据
comments_df = pd.read_csv('comments_cleaned.csv')
threads_df = pd.read_csv('threads_cleaned.csv')
engagement_df = pd.read_csv('Labeled_Developer_Activity_With_Engagement.csv')

# 预处理时间格式
comments_df['created_at'] = pd.to_datetime(comments_df['created_at'], errors='coerce')
threads_df['thread_start'] = pd.to_datetime(threads_df['thread_start'], errors='coerce')
engagement_df['last_active_month'] = pd.to_datetime(engagement_df['last_active_month'], errors='coerce')

# 标准化 issue_number 类型
comments_df['issue_number'] = comments_df['issue_number'].astype(str)
threads_df['issue_number'] = threads_df['issue_number'].astype(str)

# 合并获取 thread_start
merged_df = comments_df.merge(
threads_df[['repo', 'issue_number', 'thread_start']],
on=['repo', 'issue_number'], how='inner'
)

# 计算响应时间（天）
merged_df['response_latency'] = (merged_df['created_at'] - merged_df['thread_start']).dt.total_seconds() / 86400
merged_df['month'] = merged_df['thread_start'].dt.to_period('M').dt.to_timestamp()

# 合并 engagement 数据
merged_all = merged_df.merge(
engagement_df[['commenter', 'last_active_month', 'engagement_label']],
on='commenter', how='inner'
)

# 计算相对月份差
merged_all['month_diff'] = (
merged_all['month'].dt.to_period('M') - merged_all['last_active_month'].dt.to_period('M')
).apply(lambda x: x.n)

# 筛选 T-12 到 T
filtered_latency_df = merged_all[(merged_all['month_diff'] >= -12) & (merged_all['month_diff'] <= 0)]

# 分组统计中位数响应时间
grouped_latency = filtered_latency_df.groupby(['month_diff', 'engagement_label'])['response_latency'].median().reset_index()

# 绘图
plt.figure(figsize=(9, 5))
sns.lineplot(data=grouped_latency, x='month_diff', y='response_latency', hue='engagement_label', marker='o')
plt.title('Median Issue Response Latency From T–12 to T')
plt.xlabel('Relative Month (T)')
plt.ylabel('Median Response Latency (Days)')
plt.xticks(range(-12, 1))
plt.grid(True)
plt.tight_layout()
plt.show()
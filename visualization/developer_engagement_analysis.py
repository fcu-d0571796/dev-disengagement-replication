
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load datasets
activity_df = pd.read_csv("Labeled_Developer_Activity_With_Engagement.csv")
comments_df = pd.read_csv("comments_cleaned.csv", parse_dates=["created_at"], encoding='ISO-8859-1')
issues_df = pd.read_csv("issues_cleaned.csv", parse_dates=["created_at", "closed_at"])

# ------------------ Commit Trend Plot ------------------

# Convert month column to datetime
activity_df["month"] = pd.to_datetime(activity_df["month"])

# Compute monthly average commit count for engaged and disengaged developers
commit_trend = activity_df.groupby(["is_engaged", "month"])["commit_count"].mean().reset_index()

# ------------------ Response Latency ------------------

# Merge comments with issue creation time
merged_latency = pd.merge(comments_df, issues_df[['issue_id', 'created_at']], on='issue_id', suffixes=('', '_issue'))

# Calculate latency in days
merged_latency["latency_days"] = (merged_latency["created_at"] - merged_latency["created_at_issue"]).dt.total_seconds() / 86400

# Filter out invalid latencies
merged_latency = merged_latency[(merged_latency["latency_days"] >= 0) & (merged_latency["latency_days"] <= 100)]

# Extract month
merged_latency["month"] = merged_latency["created_at"].dt.to_period("M").dt.to_timestamp()

# Get latest engagement label
activity_latest = activity_df[activity_df["month"] == activity_df["month"].max()][["developer", "is_engaged"]]

# Join latency with developer engagement
latency_t1 = pd.merge(merged_latency, activity_latest, on="developer")

# ------------------ Bug Fix Duration ------------------

# Filter and compute duration
issues_df = issues_df.dropna(subset=["closed_at"])
issues_df["duration_days"] = (issues_df["closed_at"] - issues_df["created_at"]).dt.total_seconds() / 86400

# Merge with engagement label
bug_df = pd.merge(issues_df, activity_latest, on="developer")

# ------------------ Plotting ------------------

# Set seaborn style
sns.set(style="whitegrid")
fig, axs = plt.subplots(3, 1, figsize=(12, 18))

# Plot 1: Commit Trend
sns.lineplot(data=commit_trend, x="month", y="commit_count", hue="is_engaged", ax=axs[0])
axs[0].set_title("Monthly Commit Count Trends")
axs[0].set_ylabel("Average Commits")
axs[0].legend(title="Engagement")

# Plot 2: Response Latency (log)
sns.violinplot(data=latency_t1, x="is_engaged", y=np.log1p(latency_t1["latency_days"]), ax=axs[1])
axs[1].set_title("Response Latency at T-1 (log scale)")
axs[1].set_ylabel("log(1 + Latency Days)")
axs[1].set_xticklabels(["Disengaged", "Engaged"])

# Plot 3: Bug Fix Duration (log)
sns.violinplot(data=bug_df, x="is_engaged", y=np.log1p(bug_df["duration_days"]), ax=axs[2])
axs[2].set_title("Bug Fix Duration (log scale)")
axs[2].set_ylabel("log(1 + Duration Days)")
axs[2].set_xticklabels(["Disengaged", "Engaged"])

# Final adjustments
plt.tight_layout()
plt.savefig("developer_engagement_metrics.png")
plt.show()


# === Additional Analysis: Sentiment Trends Over Time ===
import seaborn as sns
sentiment_df = pd.read_csv('monthly_sentiment.csv')
sentiment_df['month'] = pd.to_datetime(sentiment_df['month'])
plt.figure(figsize=(10,6))
sns.lineplot(data=sentiment_df, x='month', y='sentiment_compound', hue='engagement_label', estimator='mean')
plt.title('Monthly Sentiment Trend by Engagement Status')
plt.ylabel('Average Compound Sentiment')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('sentiment_trend_by_engagement.png')
plt.close()

# === Additional Analysis: PR Success Rate ===
pr_success_df = pd.read_csv('PR_Success_Rate_Statistical_Results__T-12_to_T_.csv')
pr_success_df['month'] = pd.to_datetime(pr_success_df['month'])
plt.figure(figsize=(10,6))
sns.lineplot(data=pr_success_df, x='month', y='pr_success_rate', hue='engagement_label', estimator='mean')
plt.title('PR Success Rate Over Time by Engagement Status')
plt.ylabel('Average PR Success Rate')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('pr_success_rate_by_engagement.png')
plt.close()

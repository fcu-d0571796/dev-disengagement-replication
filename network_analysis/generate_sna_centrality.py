import pandas as pd
import networkx as nx

# 读取数据
comments_df = pd.read_csv("comments_cleaned.csv", encoding="ISO-8859-1")
threads_df = pd.read_csv("threads_cleaned.csv")
dev_activity_df = pd.read_csv("Labeled_Developer_Activity_With_Engagement.csv")

# 合并评论者标签
comments_df = comments_df.merge(
    dev_activity_df[["commenter", "engagement_label"]],
    on="commenter",
    how="left"
)
comments_df = comments_df[comments_df["engagement_label"].isin(["Engaged", "Disengaged"])]

# 构建 thread 内开发者互动边
thread_participants = (
    comments_df.groupby(["repo", "issue_number"])["commenter"]
    .unique()
    .reset_index(name="participants")
)

edges = []
for _, row in thread_participants.iterrows():
    repo, participants = row["repo"], list(row["participants"])
    edges += [(repo, a, b) for i, a in enumerate(participants) for b in participants[i+1:] if a != b]

edges_df = pd.DataFrame(edges, columns=["repo", "from", "to"])

# 添加开发者的 engagement label
edges_df = edges_df.merge(dev_activity_df[["commenter", "engagement_label"]], left_on="from", right_on="commenter", how="left")
edges_df = edges_df.rename(columns={"engagement_label": "from_label"})
edges_df = edges_df.merge(dev_activity_df[["commenter", "engagement_label"]], left_on="to", right_on="commenter", how="left")
edges_df = edges_df.rename(columns={"engagement_label": "to_label"})
edges_df.drop(columns=["commenter_x", "commenter_y"], inplace=True)

# 构建无向图
G = nx.Graph()
G.add_edges_from(edges_df[["from", "to"]].itertuples(index=False, name=None))

# 添加节点标签
for node in G.nodes():
    label = dev_activity_df.loc[dev_activity_df["commenter"] == node, "engagement_label"].values
    if label.size > 0:
        G.nodes[node]["engagement_label"] = label[0]

# 计算中心性指标
degree = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G)
try:
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
except:
    eigenvector = {n: 0 for n in G.nodes}

# 汇总为 DataFrame
centrality_df = pd.DataFrame({
    "developer": list(G.nodes),
    "degree": [degree.get(n, 0) for n in G.nodes],
    "betweenness": [betweenness.get(n, 0) for n in G.nodes],
    "eigenvector": [eigenvector.get(n, 0) for n in G.nodes],
})
centrality_df = centrality_df.merge(dev_activity_df[["commenter", "engagement_label"]], left_on="developer", right_on="commenter", how="left")
centrality_df.drop(columns="commenter", inplace=True)

# 保存结果
centrality_df.to_csv("Developer_Centrality_Results.csv", index=False)

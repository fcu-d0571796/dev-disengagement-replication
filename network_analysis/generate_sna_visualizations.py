import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

# 读取数据
comments_df = pd.read_csv("comments_cleaned.csv", encoding="ISO-8859-1")
threads_df = pd.read_csv("threads_cleaned.csv")
dev_activity_df = pd.read_csv("Labeled_Developer_Activity_With_Engagement.csv")

# 合并 engagement 标签
comments_df = comments_df.merge(
    dev_activity_df[["commenter", "engagement_label"]],
    on="commenter", how="left"
)
comments_df = comments_df[comments_df["engagement_label"].isin(["Engaged", "Disengaged"])]

# 互动边构建
thread_participants = (
    comments_df.groupby(["repo", "issue_number"])["commenter"]
    .unique().reset_index(name="participants")
)

edges = []
for _, row in thread_participants.iterrows():
    repo, participants = row["repo"], list(row["participants"])
    edges += [(repo, a, b) for i, a in enumerate(participants)
              for b in participants[i+1:] if a != b]

edges_df = pd.DataFrame(edges, columns=["repo", "from", "to"])

# 边计数（互动次数）
edge_weights = edges_df.groupby(["from", "to"]).size().reset_index(name="weight")

# Global SNA 图（过滤 weight >= 3 且 degree > 1）
G = nx.Graph()
for _, row in edge_weights.iterrows():
    if row["weight"] >= 3:
        G.add_edge(row["from"], row["to"], weight=row["weight"])

# 添加 engagement label
labels_dict = dev_activity_df.set_index("commenter")["engagement_label"].to_dict()
nx.set_node_attributes(G, labels_dict, "engagement_label")

# 删除度为 1 的节点
nodes_to_remove = [n for n, d in dict(G.degree()).items() if d <= 1]
G.remove_nodes_from(nodes_to_remove)

# 绘制全局图
plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, seed=42)
colors = {"Engaged": "#377eb8", "Disengaged": "#e41a1c"}
node_colors = [colors.get(G.nodes[n].get("engagement_label", "gray")) for n in G.nodes()]
nx.draw(G, pos, node_color=node_colors, edge_color="lightgray", with_labels=False, node_size=30)
plt.title("Global SNA Graph (Edge weight ≥ 3, Degree > 1)")
plt.savefig("global_sna_graph_filtered.png", dpi=300)
plt.close()

# pytorch/pytorch 图（不去除弱节点）
pt_edges = edges_df[edges_df["repo"] == "pytorch/pytorch"]
pt_graph = nx.Graph()
pt_graph.add_edges_from(pt_edges[["from", "to"]].itertuples(index=False, name=None))
nx.set_node_attributes(pt_graph, labels_dict, "engagement_label")

# 绘制 pytorch 全图
plt.figure(figsize=(12, 10))
pos = nx.spring_layout(pt_graph, seed=42)
node_colors = [colors.get(pt_graph.nodes[n].get("engagement_label", "gray")) for n in pt_graph.nodes()]
nx.draw(pt_graph, pos, node_color=node_colors, edge_color="lightgray", with_labels=False, node_size=30)
plt.title("Full Interaction Network for pytorch/pytorch")
plt.savefig("pytorch_full_graph.png", dpi=300)
plt.close()

# 中心性分布图
centrality_df = pd.read_csv("Developer_Centrality_Results.csv")
centrality_df = centrality_df[centrality_df["engagement_label"].isin(["Engaged", "Disengaged"])]

# 绘制中心性指标分布
plt.figure(figsize=(12, 6))
melted = centrality_df.melt(id_vars="engagement_label", value_vars=["degree", "betweenness", "eigenvector"],
                            var_name="Centrality", value_name="Score")
sns.boxplot(data=melted, x="Centrality", y="Score", hue="engagement_label", palette=colors)
plt.title("Distribution of Centrality Metrics by Engagement Label")
plt.legend(title="Engagement")
plt.tight_layout()
plt.savefig("centrality_distributions.png", dpi=300)
plt.close()

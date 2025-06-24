import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: 读取数据
df = pd.read_csv('Aggregated_Churn_By_Commenter.csv')

# Step 2: 选择数值特征进行聚类（排除非数值或ID列）
features = [
    'churn_add_mean', 'churn_add_sum', 'churn_add_std',
    'churn_del_mean', 'churn_del_sum', 'churn_del_std',
    'total_churn_mean', 'total_churn_sum', 'churn_ratio_mean',
    'active_months_max'
]
X = df[features].fillna(0)  # 填补可能的缺失值

# Step 3: 标准化特征
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 4: KMeans 聚类（这里设 k=4，可调）
k = 3
kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
df['cluster'] = kmeans.fit_predict(X_scaled)

# Step 5: PCA 降维用于可视化
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
df['pca1'] = X_pca[:, 0]
df['pca2'] = X_pca[:, 1]

# Step 6: 可视化聚类结果
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='pca1', y='pca2', hue='cluster', palette='Set2', s=60)
plt.title('KMeans Clustering of Developer Code Churn Patterns')
plt.xlabel('PCA 1')
plt.ylabel('PCA 2')
plt.legend(title='Cluster')
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 7: 打印每个 cluster 的平均特征值（可了解模式差异）
cluster_summary = df.groupby('cluster')[features].mean().round(2)
print("\n🔍 Cluster Summary:")
print(cluster_summary)


import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: 读取数据
df = pd.read_csv('Aggregated_Churn_By_Commenter.csv')

# Step 2: 提取精选特征
features = [
    'churn_add_mean',
    'churn_del_mean',
    'churn_ratio_mean',
    'total_churn_mean',
    'active_months_max'
]
X = df[features].fillna(0)

# Step 3: 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 4: KMeans 聚类
k = 3  # 可以从3开始试验
kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
df['cluster'] = kmeans.fit_predict(X_scaled)

# Step 5: PCA 可视化
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
df['pca1'] = X_pca[:, 0]
df['pca2'] = X_pca[:, 1]

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='pca1', y='pca2', hue='cluster', palette='Set1', s=60)
plt.title('Developer Churn Pattern Clustering (Selected Features)')
plt.xlabel('PCA 1')
plt.ylabel('PCA 2')
plt.legend(title='Cluster')
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 6: 输出每个 cluster 的均值，观察行为差异
cluster_summary = df.groupby('cluster')[features + ['engagement_label_first']].mean(numeric_only=True).round(2)
print("\n🔍 Cluster Summary:")
print(cluster_summary)

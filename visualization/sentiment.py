import nltk
nltk.download('vader_lexicon')

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# 仅需第一次执行
nltk.download('vader_lexicon')

# 读取你的CSV文件
df = pd.read_csv('comments_cleaned.csv')

# 去除无效行
df = df.dropna(subset=['body'])

# 初始化分析器
sid = SentimentIntensityAnalyzer()

# 计算每条评论的 compound 分数
df['sentiment_compound'] = df['body'].apply(lambda x: sid.polarity_scores(str(x))['compound'])

# 可选：按月统计每位开发者的平均情绪
df['created_at'] = pd.to_datetime(df['created_at'])
df['month'] = df['created_at'].dt.to_period('M')
monthly_sentiment = df.groupby(['commenter', 'month'])['sentiment_compound'].mean().reset_index()

# 保存结果
df.to_csv('comments_with_sentiment.csv', index=False)
monthly_sentiment.to_csv('monthly_sentiment.csv', index=False)
import pandas as pd
import numpy as np
from transformers import pipeline
import re
from tqdm import tqdm

# 设置 tqdm 用于 pandas apply 的进度条
tqdm.pandas()

# =====================
# Step 1: 读取与清洗数据
# =====================

# 替换为你的 CSV 路径
df = pd.read_csv("your_file.csv")  # 或者 pd.read_excel("your_file.xlsx")

# 查看数据结构
print(df.columns)
print(df.shape)

# 清洗空白评论、全是标点/空格的评论
def is_valid_text(text):
    if pd.isna(text): return False
    cleaned = re.sub(r'[\s\W_]+', '', text)
    return len(cleaned) > 5  # 保证不是太短

df = df[df["body"].apply(is_valid_text)].copy()

# 去除重复内容（可选）
df.drop_duplicates(subset=["body"], inplace=True)

# 简单清洗文本
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)              # 多个空格变一个
    text = re.sub(r'<[^>]+>', '', text)           # 去HTML
    text = re.sub(r'[^\x00-\x7F]+', '', text)     # 去非ASCII字符
    return text.strip()

df["cleaned_body"] = df["body"].apply(clean_text)

# 保存清洗后的数据（包含 cleaned_body 列）
df.to_csv("cleaned_comments.csv", index=False)

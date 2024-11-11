import pandas as pd
import numpy as np
from outlier import (
    df_outliers_iqr,
    df_outliers_mad,
    df_outliers_none,
)

import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("toal_data.csv")
from scipy.stats import pearsonr
df = df.drop(df[df["year"] == 2011].index)
df = df.set_index(["county", "year"])
total = 0
result_list = []
for c in df.columns:
    if c == "wheat_yield":
        continue
    if c == "winter_wheat_yield":
        result = df_outliers_none(df, variable=c, group_by="county")
        result_list.append(result)
        continue
    result = df_outliers_none(df, variable=c, group_by="county", fill_method="median", threshold=2.5)
    
    result_list.append(result)
    
    correlation, p_value = pearsonr(result, df["winter_wheat_yield"])
    print(f"{c} 皮尔逊相关系数: {correlation} p 值: {p_value}")
    total += abs(correlation)

result = pd.concat(result_list, axis=1)

result.to_csv("outlier_result.csv")
correlation_matrix = result.corr(method="pearson").round(2)

plt.figure(figsize=(15, 12))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title(f"mad 1 {total}")
plt.show()
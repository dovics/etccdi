import pandas as pd

def delta_change(df: pd.DataFrame, base_df: pd.DataFrame, variable: str) -> pd.DataFrame:
    # 假设 df 和 base_df 中有一个时间列 'year'
    df_2020_2025 = df[(df['year'] >= 2020) & (df['year'] <= 2025)]
    
    # 计算 2020-2025 年的最小值和最大值
    base_min = base_df[variable].min()
    base_max= base_df[variable].max()
    
    df_min_2020_2025 = df_2020_2025[variable].min()
    df_max_2020_2025 = df_2020_2025[variable].max()
    
    # 应用最小-最大归一化公式，将 2020-2025 年的数据缩放到新的范围
    df.loc[(df['year'] >= 2020) & (df['year'] <= 2025), variable] = (
        (df_2020_2025[variable] - df_min_2020_2025) / (df_max_2020_2025 - df_min_2020_2025)
    ) * (base_max - base_min) + base_min
    
    # 计算缩放比例
    scale_factor = (base_max - base_min) / (df_max_2020_2025 - df_min_2020_2025)
    offset = base_min - scale_factor * df_min_2020_2025
    
    # 将缩放比例应用到其他年份的数据
    df.loc[(df['year'] < 2020) | (df['year'] > 2025), variable] = (
        df.loc[(df['year'] < 2020) | (df['year'] > 2025), variable] * scale_factor + offset
    )
    
    return df
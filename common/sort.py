import pandas as pd
from config import country_list

country_order = {name: idx for idx, name in enumerate(country_list)}
def sort_by_contry(df: pd.DataFrame) -> pd.DataFrame:
    if 'name' in df.index.names: 
        copy_df = df.reset_index()
    else:
        copy_df = df.copy()
    copy_df['order_key'] = copy_df['name'].map(country_order)
    if 'year' in copy_df.columns:
        by = ["order_key", "year"]
    else:
        by = ["order_key"]
    return copy_df.sort_values(by=by, na_position='last').drop('order_key', axis=1)
import pandas as pd
import glob
from pathlib import Path

folder_path = 'result_data'

csv_files = glob.glob(f'{folder_path}/*.csv')
def get_var(file_path):
    file_name = Path(file_path).stem
    if file_name.endswith('_era5'):
        file_name = file_name[:-5] 
    return file_name

get_file_name = lambda x: Path(x).stem
df_list = [pd.read_csv(file, index_col=["name", "year"]).rename(columns={"value": get_var(file)}) for file in csv_files]
combined_df = pd.concat(df_list, axis=1)
combined_df = combined_df[combined_df.index.get_level_values('year') >= 1989] 
combined_df.to_csv('combined_result.csv', float_format='%.2f')
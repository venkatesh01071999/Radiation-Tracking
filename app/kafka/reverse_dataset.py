import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

input_path = os.environ.get('CHUNK_FILE')

df = pd.read_csv(input_path, low_memory=False)

df_reversed = df.iloc[::-1].reset_index(drop=True)

df_reversed.to_csv(os.environ.get('PROCESSED_FILE'), index=False)

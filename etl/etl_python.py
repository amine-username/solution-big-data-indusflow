import pandas as pd
import os

folder = "data"

for file in os.listdir(folder):
    if file.endswith(".csv"):
        path = folder + "/" + file

        df = pd.read_csv(path)
        df = df.drop_duplicates()
        df = df.dropna()
        
        df.to_csv("data_clean/" + file, index=False)

        

        print(file, "OK - lignes clean:", len(df))






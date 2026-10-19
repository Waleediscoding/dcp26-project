import pandas as pd
import sqlite3

df = pd.read_csv("dataset/productivity_metrics.csv")

conn = sqlite3.connect("database/data.db")

df.to_sql("productivity_metrics", conn, if_exists="replace", index=False)

query_data = pd.read_sql("SELECT * FROM productivity_metrics", conn)

print(query_data)
conn.close()
from application import SceneManager

app = SceneManager(title="Dashboard", w=800, h=600)

app.mainloop()

# Some SQL queries (commented out as they don't contribute to the application)
"""
try:
    conn = sqlite3.connect("database/data.db")
    df1 = pd.read_sql("SELECT Productivity, COUNT(Productivity) as productivity_count FROM productivity_metrics GROUP BY Productivity", conn)
    df2 = pd.read_sql(
        'SELECT AVG("Reading (Minutes)") as Reading, AVG("Gaming (Minutes)") as Gaming, AVG("Programming (Minutes)") as Programming FROM productivity_metrics', conn
    )
    df3 = pd.read_sql(
        'SELECT Date, "Misc Leisure (Minutes)" FROM productivity_metrics WHERE "Misc Leisure (Minutes)" > 300', conn
    )
    
    print(df1)
    print(df2)
    print(df3)
    
    # Un-comment these for a visual representation
    # x1, height1 = df1["Productivity"], df1["productivity_count"]
    
    # plt.bar(x=x1, height=height1)
    # plt.title("Count of Each Productivity Class")
    # plt.xlabel("Class")
    # plt.ylabel("#")
    # plt.xticks(rotation=90, ha="right")
    # plt.tight_layout()
    # plt.show()
    
    # x2 = [colname for colname in df2]
    # height2 = [x for colname in df2 for x in df2[colname]]
    
    # plt.bar(x=x2, height=height2)
    # plt.title("Number of minutes spent on each category on average")
    # plt.xlabel("Categories")
    # plt.ylabel("Minutes")
    # plt.xticks(rotation=0, ha="center")
    # plt.tight_layout()
    # plt.show()
    
    # x3 = df3["Date"]
    # y3 = df3["Misc Leisure (Minutes)"]
    
    # plt.plot(x3, y3, marker='o')
    # plt.title("Misc Leisure over 300 minutes")
    # plt.xlabel("Days")
    # plt.ylabel("Minutes")
    # plt.xticks(rotation=90)
    # plt.tight_layout()
    # plt.show()
finally:
    conn.close()
"""
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="sql_automation",
        user="u0_a509",
        host="127.0.0.1",   # 🔥 IMPORTANT
        port="5432"         # 🔥 IMPORTANT
    )

    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user;")
    result = cur.fetchone()

    print("Connected successfully!")
    print("Database:", result[0])
    print("User:", result[1])

    cur.close()
    conn.close()

except Exception as e:
    print("Connection failed")
    print(e)

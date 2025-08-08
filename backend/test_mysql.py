import pymysql

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='thanuja',
        database='toolinformation',
        port=3306
    )
    print("Connected!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
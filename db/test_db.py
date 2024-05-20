import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect("host=localhost dbname=contacts user=postgres password=postgres")

# Open a cursor to perform database operations
cur = conn.cursor()
conn.autocommit = True
try:
    cur.execute("INSERT INTO Emails (ID, Email) VALUES (%s, %s)", (1, str(89999999999)))
    print('yes')
except:
    print('no')

ans = 'Список телефонов: \n'
cur.execute("SELECT * FROM Emails;")
phones = cur.fetchall()
for phone in phones:
    ans += str(phone[0]) + ' - ' + str(phone[1]) + '\n'
print(ans)
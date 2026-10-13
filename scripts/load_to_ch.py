import psycopg2
from clickhouse_driver import Client
import time

print("=== Загрузка данных из PostgreSQL в ClickHouse ===\n")

# 1. Подключение к PostgreSQL
pg_conn = psycopg2.connect(host="localhost", database="dwh", user="airflow", password="airflow")
pg_cur = pg_conn.cursor()

# 2. Подключение к ClickHouse (с паролем 123)
ch = Client(host='localhost', port=9000, database='large', user='default', password='123')

# 3. Читаем из PostgreSQL
print("1. Чтение данных из PostgreSQL...")
t0 = time.perf_counter()
pg_cur.execute("""
    SELECT order_id, order_date, region, amount, quantity
    FROM large.orders
    ORDER BY order_id
""")
rows = pg_cur.fetchall()
t1 = time.perf_counter()
print(f"   Прочитано {len(rows)} строк за {t1-t0:.2f} сек\n")

# 4. Загружаем в вариант 1
print("2. Загрузка в orders_v1 (ORDER BY order_date, region)...")
t0 = time.perf_counter()
ch.execute("INSERT INTO large.orders_v1 VALUES", rows, types_check=True)
t1 = time.perf_counter()
print(f"   Загружено за {t1-t0:.2f} сек\n")

# 5. Загружаем в вариант 2
print("3. Загрузка в orders_v2 (ORDER BY region, order_date)...")
t0 = time.perf_counter()
ch.execute("INSERT INTO large.orders_v2 VALUES", rows, types_check=True)
t1 = time.perf_counter()
print(f"   Загружено за {t1-t0:.2f} сек\n")

# 6. Проверка
print("4. Проверка количества строк:")
for tbl in ['orders_v1', 'orders_v2', 'mart_daily_sales']:
    cnt = ch.execute(f"SELECT count() FROM large.{tbl}")[0][0]
    print(f"   {tbl}: {cnt:,} строк")

pg_cur.close()
pg_conn.close()
print("\n✅ Загрузка завершена!")

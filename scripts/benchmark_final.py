import psycopg2
from clickhouse_driver import Client
import time

print("=" * 70)
print("БЕНЧМАРК: PostgreSQL vs ClickHouse (5 повторений)")
print("=" * 70)

# --- PostgreSQL ---
pg = psycopg2.connect(host="localhost", database="dwh", user="airflow", password="airflow")
pg_cur = pg.cursor()
pg_cur.execute("ANALYZE large.orders;") # Актуальная статистика

queries_pg = {
    "PG Узкий (1 мес)": "SELECT region, SUM(amount), COUNT(*) FROM large.orders WHERE order_date BETWEEN '2023-06-01' AND '2023-06-30' GROUP BY region ORDER BY SUM(amount) DESC",
    "PG Широкий (2 года)": "SELECT region, SUM(amount), COUNT(*) FROM large.orders WHERE order_date BETWEEN '2022-01-01' AND '2023-12-31' GROUP BY region ORDER BY SUM(amount) DESC"
}

print("\n[PostgreSQL]")
for name, sql in queries_pg.items():
    pg_cur.execute(sql); pg_cur.fetchall() # Прогрев
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        pg_cur.execute(sql); pg_cur.fetchall()
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    print(f"  {name:20} | min: {times[0]:6.2f}ms | med: {times[2]:6.2f}ms | max: {times[4]:6.2f}ms")

# --- ClickHouse ---
ch = Client(host='localhost', port=9000, database='large', user='default', password='123')

queries_ch = {
    "CH Узкий (v1)": "SELECT region, sum(amount), count() FROM large.orders_v1 WHERE order_date BETWEEN '2023-06-01' AND '2023-06-30' GROUP BY region ORDER BY sum(amount) DESC",
    "CH Широкий (v1)": "SELECT region, sum(amount), count() FROM large.orders_v1 WHERE order_date BETWEEN '2022-01-01' AND '2023-12-31' GROUP BY region ORDER BY sum(amount) DESC",
    "CH Витрина (MV)": "SELECT region, total_revenue, order_count FROM large.mart_daily_sales WHERE order_date BETWEEN '2023-06-01' AND '2023-06-30' ORDER BY total_revenue DESC"
}

print("\n[ClickHouse]")
for name, sql in queries_ch.items():
    ch.execute(sql) # Прогрев
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        ch.execute(sql)
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    print(f"  {name:20} | min: {times[0]:6.2f}ms | med: {times[2]:6.2f}ms | max: {times[4]:6.2f}ms")

pg_cur.close()
pg.close()
print("\n✅ Бенчмарк завершен!")

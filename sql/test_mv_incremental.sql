-- 1. Смотрим, есть ли данные за 15 октября 2023 (должно быть пусто или 0)
SELECT 'BEFORE INSERT' AS stage, region, total_revenue, order_count
FROM large.mart_daily_sales
WHERE order_date = '2023-10-15';

-- 2. Вставляем новую пачку из 3 заказов (имитация прихода новых данных)
INSERT INTO large.orders_v1 VALUES
    (600001, '2023-10-15', 'North', 250.00, 3),
    (600002, '2023-10-15', 'South', 180.00, 2),
    (600003, '2023-10-15', 'North', 100.00, 1);

-- 3. Проверяем витрину СРАЗУ ПОСЛЕ вставки. 
-- SummingMergeTree должен был автоматически просуммировать North (250+100 = 350)
SELECT 'AFTER INSERT' AS stage, region, total_revenue, order_count
FROM large.mart_daily_sales
WHERE order_date = '2023-10-15'
ORDER BY region;

-- 4. Финальная проверка: сумма в витрине должна равняться сумме в исходной таблице
SELECT 'CONSISTENCY CHECK' AS test,
    (SELECT sum(total_revenue) FROM large.mart_daily_sales WHERE order_date = '2023-10-15') AS mv_sum,
    (SELECT sum(amount) FROM large.orders_v1 WHERE order_date = '2023-10-15') AS raw_sum,
    abs((SELECT sum(total_revenue) FROM large.mart_daily_sales WHERE order_date = '2023-10-15') - 
        (SELECT sum(amount) FROM large.orders_v1 WHERE order_date = '2023-10-15')) AS diff;

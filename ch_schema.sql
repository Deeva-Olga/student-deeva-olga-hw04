CREATE DATABASE IF NOT EXISTS large ENGINE = Atomic;

CREATE TABLE IF NOT EXISTS large.orders_v1 (
    order_id UInt64,
    order_date Date,
    region LowCardinality(String),
    amount Decimal(10, 2),
    quantity UInt32
) ENGINE = MergeTree()
ORDER BY (order_date, region)
PARTITION BY toYYYYMM(order_date);

CREATE TABLE IF NOT EXISTS large.orders_v2 (
    order_id UInt64,
    order_date Date,
    region LowCardinality(String),
    amount Decimal(10, 2),
    quantity UInt32
) ENGINE = MergeTree()
ORDER BY (region, order_date)
PARTITION BY toYYYYMM(order_date);

CREATE TABLE IF NOT EXISTS large.mart_daily_sales (
    order_date Date,
    region LowCardinality(String),
    total_revenue Decimal(18, 2),
    order_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (order_date, region);

CREATE MATERIALIZED VIEW IF NOT EXISTS large.mv_daily_sales
TO large.mart_daily_sales
AS
SELECT
    order_date,
    region,
    sum(amount) AS total_revenue,
    count() AS order_count
FROM large.orders_v1
GROUP BY order_date, region;

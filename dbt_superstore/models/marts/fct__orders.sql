{{ config(
    materialized='table'
) }}

WITH orders AS (
    -- Select all data from the cleaned orders staging table
    SELECT *
    FROM {{ ref('stg__orders') }}
),

returns AS (
    -- Select data from the cleaned returns staging table
    SELECT *
    FROM {{ ref('stg__returns') }}
),

final AS (
    SELECT
        o.*, -- Select all columns from the orders table

        -- Perform a LEFT JOIN to add the return flag
        -- Use COALESCE to set 'is_returned' to FALSE if there is no match in the returns table
        COALESCE(r.is_returned, FALSE) AS is_returned_flag

    FROM orders o
    LEFT JOIN returns r
        ON o.order_id = r.order_id

    -- Note: Since the returns table is at the order_id level (not order_item_key),
    -- dbt will join all returned rows from the orders table correctly.
    -- If multiple items in an order were returned, they will all share the same 'order_id'
    -- and will correctly be flagged as TRUE here.
)

SELECT * FROM final
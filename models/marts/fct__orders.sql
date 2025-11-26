
WITH orders AS (
    SELECT *
    FROM {{ ref('stg__orders') }}
),

returns AS (
    SELECT *
    FROM {{ ref('stg__returns') }}
),

final AS (
    SELECT
        o.*, 
        COALESCE(r.is_returned, FALSE) AS is_returned_flag

    FROM orders o
    LEFT JOIN returns r
        ON o.order_id = r.order_id


)

SELECT * FROM final

WITH source AS (

    SELECT *
    FROM {{ source('raw', 'returns') }}

),

renamed AS (

    SELECT
        "Order ID" AS order_id,

        CASE
            WHEN "Returned" = 'Yes' THEN TRUE
            ELSE FALSE
        END AS is_returned

    FROM source
)

SELECT * FROM renamed
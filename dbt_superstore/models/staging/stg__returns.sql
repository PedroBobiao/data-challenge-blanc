{{ config(
    materialized='view'
) }}

WITH source AS (

    SELECT *
    FROM {{ source('raw', 'returns') }}

),

renamed AS (

    SELECT
        -- Foreign Key
        "Order ID" AS order_id,

        -- Flag: Check for 'Yes' and convert to a boolean or integer flag
        CASE
            WHEN "Returned" = 'Yes' THEN TRUE
            ELSE FALSE
        END AS is_returned

    FROM source
)

SELECT * FROM renamed
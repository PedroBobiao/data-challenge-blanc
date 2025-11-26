{{ config(
    materialized='view'
) }}

WITH source AS (

    SELECT *
    FROM {{ source('raw', 'orders') }}

),

renamed AS (

    SELECT
        -- Primary Key
        {{ dbt_utils.surrogate_key(['"Row ID"', '"Order ID"']) }} AS order_item_key,

        -- Foreign Keys
        "Row ID" AS order_row_id,
        "Order ID" AS order_id,
        "Customer ID" AS customer_id,
        "Product ID" AS product_id,

        -- Dates
        CAST("Order Date" AS DATE) AS order_date,
        CAST("Ship Date" AS DATE) AS ship_date,

        -- Dimensions
        "Ship Mode" AS ship_mode,
        "Customer Name" AS customer_name,
        "Segment" AS segment,
        "Country/Region" AS country_region,
        "City" AS city,
        "State" AS state,
        -- Coalesce to handle potential nulls, then cast to string for key-like columns
        COALESCE(CAST("Postal Code" AS VARCHAR), 'N/A') AS postal_code,
        "Region" AS region,
        "Category" AS category,
        "Sub-Category" AS sub_category,
        "Product Name" AS product_name,

        -- Facts
        CAST("Sales" AS NUMERIC) AS sales,
        CAST("Quantity" AS INTEGER) AS quantity,
        CAST("Discount" AS NUMERIC) AS discount,
        CAST("Profit" AS NUMERIC) AS profit

    FROM source
)

SELECT * FROM renamed
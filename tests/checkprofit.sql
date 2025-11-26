SELECT 
    *
FROM 
    {{ ref('fct__orders') }} 
WHERE 
    discount > 0.0 
    AND profit < 0.0
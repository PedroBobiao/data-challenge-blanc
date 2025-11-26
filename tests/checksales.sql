select *
from {{ ref('fct__orders') }} 
where sales <0
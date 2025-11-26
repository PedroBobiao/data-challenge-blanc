select *
from {{ ref('stg__orders') }}
where quantity <0
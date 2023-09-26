
select
    date_trunc('day', created_at) as day
    , product_id
    , count(product_id) as nb_prod_ordered_day

from raw.public.orders
left join raw.public.order_items
    using(order_id)
where product_id = '74aeb414-e3dd-4e8a-beef-0fa45225214d'
group by 1,2
-- 20 and 15


select
  date_trunc('day', e.created_at) as day
  ,product_id
  ,count(product_id) as nb_page_views_day


from raw.public.events e
left join raw.public.orders o
    using (order_id)
where e.event_type = 'page_view' and product_id = '74aeb414-e3dd-4e8a-beef-0fa45225214d'
group by 1, 2
-- 44 and 22
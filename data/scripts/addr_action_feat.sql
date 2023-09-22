with backup_address as(
    select * from 
    (
     select 
     from_address
     ,max(CAST(nonce AS double)) as max_nonce
     ,min(block_date) as min_date
     ,max(block_date) as max_date
     ,count(DISTINCT block_date) as day_cnt
     ,sum(receipt_gas_used * gas_price) as gas_use
     from transactions 
     group by from_address
    )where (max_date != min_date)
	and nonce >= 5
),

min_block as (
   select 
   from_address
   ,min(block_number) as block_number
   from transactions 
   where from_address!=to_address
   group by from_address
 ),
min_action as (
        SELECT
        from_address
        ,first_to_address
        ,first_methoid
        FROM
        (
                SELECT
                *
                ,row_number() over(PARTITION BY from_address ORDER BY transaction_index) as rank1
                FROM
                (
                 SELECT 
                 a.from_address
                 ,a.to_address as first_to_address
                 ,a.methoid as first_methoid
                 ,a.transaction_index
                 FROM
                 (
                   select 
                   from_address
                   ,block_number
                   ,to_address
                   ,substr(input,1,10) as methoid
                   ,transaction_index
                   from transactions 
                 )a inner join min_block b on a.from_address=b.from_address
                 and a.block_number=b.block_number
                )
        )where rank1=1
),
max_block as (
   select 
   from_address
   ,max(block_number) as block_number
   from transactions 
   where from_address!=to_address
   group by from_address
),
max_action as (
        SELECT
        from_address
        ,last_to_address
        ,last_methoid
        FROM
        (
                SELECT
                *
                ,row_number() over(PARTITION BY from_address ORDER BY transaction_index DESC) as rank1
                FROM
                (
                 SELECT 
                 a.from_address
                 ,a.to_address as last_to_address
                 ,a.methoid as last_methoid
                 ,a.transaction_index
                 FROM
                 (
                   select 
                   from_address
                   ,block_number
                   ,to_address
                   ,substr(input,1,10) as methoid
                   ,transaction_index
                   from transactions 
                 )a inner join max_block b on a.from_address=b.from_address
                 and a.block_number=b.block_number
                )
        )where rank1=1
),
action_feat as(
SELECT
a.*
,b.last_to_address
,last_methoid
FROM min_action a 
left join max_action b on a.from_address=b.from_address
)


backup_address2 as(
        select 
          a.from_address as addr, 
          concat(
                a.max_nonce, '_', a.min_date, '_', 
                a.max_date, '_', a.day_cnt, '-', c.first_to_address, 
                '-', c.first_methoid, '-', c.last_to_address, 
                '-', c.last_methoid
          ) as metric_group_id 
        from 
          backup_address a 
          inner join action_feat c on a.from_address = c.from_address
),


filter_con as(
    select 
    metric_group_id
    from backup_address2 
    group by metric_group_id
    having count(distinct addr) >= 10
)


SELECT a.*
FROM
backup_address2 a 
inner join filter_con b on a.metric_group_id=b.metric_group_id
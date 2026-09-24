-- FEE100K response-retention ownership census (read-only).
--
-- This query deliberately performs no DELETE, TRUNCATE, UPDATE, function call,
-- cron change, or threshold change.  It separates pg_net responses by the only
-- ownership fact currently proven in production: whether the response ID is
-- referenced by fee100k_http_request_v1 and whether that request is processed.
-- Unowned rows remain unsafe to reclaim until legacy consumers are resolved.

begin;
set local statement_timeout = '3000ms';

with classified as (
  select
    response.id,
    response.created,
    coalesce(octet_length(response.content), 0)::bigint as content_bytes,
    case
      when request.request_id is not null and request.processed_at is null
        then 'A_FEE100K_UNPROCESSED'
      when request.request_id is not null and request.processed_at is not null
        then 'C_FEE100K_PROCESSED'
      when request.request_id is null
           and response.created >= now() - interval '2 hours'
        then 'B_UNOWNED_RECENT_LT_2H'
      else 'D_UNOWNED_OLD_GE_2H'
    end as bucket
  from net._http_response as response
  left join public.fee100k_http_request_v1 as request
    on request.request_id = response.id
),
grouped as (
  select
    bucket,
    count(*)::bigint as rows,
    sum(content_bytes)::bigint as logical_content_bytes,
    min(created) as oldest_created,
    max(created) as newest_created
  from classified
  group by bucket
)
select jsonb_build_object(
  'observed_at', now(),
  'database_bytes', pg_database_size(current_database()),
  'response_relation_bytes',
    pg_total_relation_size('net._http_response'::regclass),
  'response_rows', (select count(*) from classified),
  'classification', coalesce(
    (select jsonb_agg(to_jsonb(grouped) order by bucket) from grouped),
    '[]'::jsonb
  )
) as result;

commit;

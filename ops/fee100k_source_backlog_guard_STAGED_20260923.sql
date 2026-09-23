-- FEE100K safeguard, STAGED ONLY: do not imply it is deployed.
-- Apply only after confirming fee100k source queue backlog and current cron state.
-- Inserts a fail-safe into the existing queue_sources function without changing
-- any source URLs, collection frequencies, fee100k thresholds, data or crons.
-- Resumes automatically when backlog drops below 30 stale SOURCE requests.
DO $$
DECLARE
  fdef text;
  marker text := E'\nbegin\n  for r in\n';
  replacement text;
BEGIN
  SELECT pg_get_functiondef(p.oid) INTO fdef
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='fee100k_private' AND p.proname='queue_sources' AND p.pronargs=0;
  IF fdef IS NULL OR position(marker IN fdef)=0
       OR position('CIRCUIT_OPEN_SOURCE_BACKLOG' IN fdef)>0
  THEN RAISE EXCEPTION 'Definition changed or safeguard already exists. No patch applied.'; END IF;
  replacement := E'\nbegin\n'
    || E'  -- Fail safe: avoid compounding a stalled SOURCE queue. Auto-resume.\n'
    || E'  if (select count(*) from\n'
    || E'    (select 1 from public.fee100k_http_request_v1\n'
    || E'     where request_kind=''SOURCE'' and processed_at is null\n'
    || E'       and created_at < now()-interval ''5 minutes'' limit 30) pending\n'
    || E'   ) >= 30 then\n'
    || E'    return jsonb_build_object(''queued'',0,\n'
    || E'       ''reason'',''CIRCUIT_OPEN_SOURCE_BACKLOG'',\n'
    || E'       ''at'',now(),''auto_resume'',true);\n'
    || E'  end if;\n  for r in\n';
  EXECUTE replace(fdef,marker,replacement);
END $$;
-- Check queue health after deploying, before considering any more changes:
-- SELECT fee100k_private.queue_sources(); (queues if backlog healthy; do not run casually)
-- SELECT count(*) FROM public.fee100k_http_request_v1
-- WHERE request_kind='SOURCE' AND processed_at IS NULL
--   AND created_at<now()-interval '5 minutes';

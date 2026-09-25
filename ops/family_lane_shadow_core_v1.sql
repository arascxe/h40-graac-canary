-- FEE100K family-lane shadow core v1
-- Created 2026-09-25. Read-only. Preserves frozen scoring thresholds.
-- Purpose: isolate the computational core of job 101 without INSERT/UPDATE.
-- Production job 101 remains unchanged.
--
-- Live shadow result, 2026-09-25 07:26 UTC:
--   completed within the 15s statement timeout (connector wall 7.2s)
--   52,639 recent births / 52,639 distinct mints / 5,322 families
--   VETO 47; SHADOW 3,635; COPY_SPAM_VETO 1,636;
--   FAMILY_EXPANSION_WATCH 4; FAMILY_EXPANSION_STRONG 0.
--
-- Main changes vs current refresh_family_lane():
--   1. Materialize the 48h birth subset once.
--   2. Resolve latest econ only for recent mints via the existing
--      (mint, observed_at desc) index.
--   3. Compute backfill-contaminated families once instead of correlated
--      EXISTS checks per output family.
--   4. Perform no upsert. A separate delta-write shadow is required before
--      any production proposal.

begin;
set local statement_timeout = '15000ms';

with
recent_births as materialized (
  select mint,name,symbol,created_at_chain,twitter,website,origin_hint,raw,family_tokens
  from public.fee100k_birth_seed_v1
  where created_at_chain >= now() - interval '48 hours'
),
recent_mints as materialized (
  select distinct mint from recent_births
),
latest_econ as materialized (
  select m.mint,e.generated_fee_24h_est_usd,e.observed_at
  from recent_mints m
  left join lateral (
    select generated_fee_24h_est_usd,observed_at
    from public.fee100k_right_tail_econ_v1 e
    where e.mint=m.mint
      and e.generated_fee_24h_est_usd is not null
    order by e.observed_at desc
    limit 1
  ) e on true
),
backfill_families as materialized (
  select distinct tok as family_key
  from recent_births b
  cross join lateral unnest(b.family_tokens) tok
  where coalesce((b.raw->>'backfill_research')::boolean,false)
),
exploded as materialized (
  select s.mint,s.name,s.symbol,s.created_at_chain,s.twitter,s.website,
         s.origin_hint,tok as family_key,le.generated_fee_24h_est_usd
  from recent_births s
  cross join lateral unnest(s.family_tokens) tok
  left join latest_econ le on le.mint=s.mint
),
agg as (
  select family_key,
         count(*) as births,
         count(distinct fee100k_private.norm_label(name)) as unique_names,
         count(distinct fee100k_private.norm_label(symbol)) as unique_symbols,
         count(*) filter (
           where coalesce(twitter,'')<>'' and coalesce(website,'')<>''
         ) as identity_n,
         count(*) filter (
           where origin_hint in (
             'DIRECT_EXTERNAL_MEDIA','EXTERNAL_LINK_HUB','X_PRETOKEN_POST'
           )
         ) as external_n,
         max(coalesce(generated_fee_24h_est_usd,0)) as leader_fee,
         (array_agg(
           coalesce(generated_fee_24h_est_usd,0)
           order by coalesce(generated_fee_24h_est_usd,0) desc
         ))[2] as second_fee,
         sum(coalesce(generated_fee_24h_est_usd,0)) as total_fee,
         count(*) filter (
           where coalesce(generated_fee_24h_est_usd,0)>=5000
         ) as n5,
         count(*) filter (
           where generated_fee_24h_est_usd<1000
         ) as nlt1
  from exploded
  group by family_key
  having count(*)>=3
),
leaders as (
  select distinct on (x.family_key)
         x.family_key,x.mint,x.name
  from exploded x
  join agg a using(family_key)
  order by x.family_key,
           coalesce(x.generated_fee_24h_est_usd,0) desc,
           x.created_at_chain
),
scored as (
  select a.*,l.mint as leader_mint,l.name as leader_name,
         a.unique_names::numeric/nullif(a.births,0) as remix_ratio,
         a.identity_n::numeric/nullif(a.births,0) as identity_ratio,
         (bf.family_key is not null) as backfill_contaminated,
         case
           when fee100k_private.hard_veto_reason(a.family_key) in (
             'ADULT_OR_SEO_SPAM','VIOLENCE_OR_TRAGEDY',
             'POLITICS_OR_CONFLICT','SPORTS'
           ) then 'VETO'
           when a.births>=4
             and a.leader_fee>=10000
             and a.unique_names::numeric/nullif(a.births,0)>=0.55
             and a.identity_n::numeric/nullif(a.births,0)>=0.50
             and coalesce(a.second_fee,0)>=1000
             and (a.external_n>=1 or a.leader_fee>=25000)
             then 'FAMILY_EXPANSION_STRONG'
           when a.births>=3
             and a.leader_fee>=5000
             and a.unique_names::numeric/nullif(a.births,0)>=0.45
             and a.identity_n::numeric/nullif(a.births,0)>=0.35
             then 'FAMILY_EXPANSION_WATCH'
           when a.births>=5
             and a.unique_names::numeric/nullif(a.births,0)<0.35
             then 'COPY_SPAM_VETO'
           else 'SHADOW'
         end as lane_state
  from agg a
  join leaders l using(family_key)
  left join backfill_families bf using(family_key)
),
state_counts as (
  select lane_state,count(*) as n
  from scored
  group by lane_state
)
select jsonb_build_object(
  'recent_births',(select count(*) from recent_births),
  'recent_mints',(select count(*) from recent_mints),
  'families',coalesce(sum(n),0),
  'states',coalesce(jsonb_object_agg(lane_state,n),'{}'::jsonb),
  'version','FAMILY_LANE_SHADOW_CORE_V1'
)
from state_counts;

rollback;

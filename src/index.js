const GECKO = 'https://api.geckoterminal.com/api/v2/networks/new_pools';
const SOLANA_RPC = 'https://api.mainnet-beta.solana.com';
const BASE_RPC = 'https://mainnet.base.org';
const SOL_PROGRAMS = {
  pumpfun_launch: '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',
  pumpswap: 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA',
  raydium_launchlab: 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj',
};
const BASE_UNIV2_FACTORY = '0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6';
const PAIR_CREATED_TOPIC0 = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9';

function nowSec(){ return Math.floor(Date.now()/1000); }
function hexInt(x){ return Number.parseInt(x||'0x0',16); }
function topicAddress(x){ return '0x'+x.replace(/^0x/,'').slice(-40).toLowerCase(); }
function wordAddress(data,idx){ const s=data.replace(/^0x/,''); const w=s.slice(idx*64,(idx+1)*64); if(w.length!==64) throw new Error('short ABI word'); return '0x'+w.slice(-40).toLowerCase(); }
function usage(){ return {queries:0,rows_read:0,rows_written:0}; }
function tally(u,meta){ u.queries++; u.rows_read += Number(meta?.rows_read||0); u.rows_written += Number(meta?.rows_written||0); }

async function dbAll(stmt,u){ const r=await stmt.all(); tally(u,r.meta); return r.results||[]; }
async function dbRun(stmt,u){ const r=await stmt.run(); tally(u,r.meta); return r; }

async function jsonFetch(url,init={}){
  const t0=Date.now(); const r=await fetch(url,init); const latency=Date.now()-t0;
  if(!r.ok){ const e=new Error(`HTTP ${r.status}`); e.status=r.status; e.latency=latency; throw e; }
  return {body:await r.json(),latency};
}
async function rpc(url,method,params){
  const {body,latency}=await jsonFetch(url,{method:'POST',headers:{'content-type':'application/json','user-agent':'h40-graac-canary/0.2'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});
  if(body.error){const e=new Error(JSON.stringify(body.error));e.latency=latency;throw e;} return {result:body.result,latency};
}
async function checkpoint(db,source,chain,stream,u){
  const rows=await dbAll(db.prepare(`SELECT * FROM source_checkpoints WHERE source=? AND chain=? AND stream_id=?`).bind(source,chain,stream),u); return rows[0]||null;
}
async function putCheckpoint(db,source,chain,stream,cursor,block,sourceTime,state,u){
  await dbRun(db.prepare(`INSERT INTO source_checkpoints(source,chain,stream_id,cursor,block_or_slot,source_time,updated_at,state_json) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source,chain,stream_id) DO UPDATE SET cursor=excluded.cursor,block_or_slot=excluded.block_or_slot,source_time=excluded.source_time,updated_at=excluded.updated_at,state_json=excluded.state_json`).bind(source,chain,stream,cursor,block,sourceTime,nowSec(),JSON.stringify(state||{})),u);
}
async function coverage(db,x,u){
  const key=`${x.source}|${x.chain}|${x.eventClass}|${x.stream}|${x.start}|${x.end}`;
  await dbRun(db.prepare(`INSERT OR REPLACE INTO coverage_windows(coverage_key,source,chain,event_class,stream_id,window_start,window_end,status,cursor_start,cursor_end,request_count,rate_limit_429_count,provider_error_count,recovery_complete,source_latency_ms,poll_lag_s,notes_json,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).bind(key,x.source,x.chain,x.eventClass,x.stream,x.start,x.end,x.status,x.cursorStart||null,x.cursorEnd||null,x.requests||0,x.r429||0,x.errors||0,x.recovery?1:0,x.latency??null,x.pollLag??null,JSON.stringify(x.notes||{}),nowSec()),u); return key;
}
async function recall(db,x,u){
  const id=`${x.source}|${x.chain}|${x.stream}|${x.eventClass}|${x.start}|${x.end}`;
  await dbRun(db.prepare(`INSERT OR REPLACE INTO recall_windows(recall_id,source,chain,stream_id,event_class,window_start,window_end,event_count,success_count,coverage_key,metadata_json,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)`).bind(id,x.source,x.chain,x.stream,x.eventClass,x.start,x.end,x.count,x.success,x.coverageKey||null,JSON.stringify(x.metadata||{}),nowSec()),u);
}
async function rawBatch(db,x,u){
  if(!x.items?.length) return;
  const id=`${x.source}|${x.chain}|${x.eventClass}|${x.start}|${x.end}`;
  await dbRun(db.prepare(`INSERT OR IGNORE INTO raw_batches(batch_id,event_time_start,event_time_end,ingest_time,source,chain,event_class,item_count,coverage_key,payload_json) VALUES(?,?,?,?,?,?,?,?,?,?)`).bind(id,x.start,x.end,x.ingest,x.source,x.chain,x.eventClass,x.items.length,x.coverageKey||null,JSON.stringify(x.items)),u);
}

async function geckoScout(env,t,u){
  const source='gecko:new_pools',chain='multi',stream='global'; const cp=await checkpoint(env.DB,source,chain,stream,u);
  let items=[],overlap=-1,requests=0,errors=0,r429=0,latency=0;
  try{for(let page=1;page<=2;page++){const z=await jsonFetch(`${GECKO}?page=${page}&include=base_token,quote_token,dex`,{headers:{accept:'application/json;version=20230203','user-agent':'h40-graac-canary/0.2'}});requests++;latency+=z.latency;const rows=z.body.data||[];const base=items.length;items.push(...rows);if(cp?.cursor){const j=rows.findIndex(r=>r.id===cp.cursor);if(j>=0){overlap=base+j;break;}}if(!rows.length)break;}}catch(e){errors++;if(e.status===429)r429++;}
  const initial=!cp; let status='PARTIAL',recovery=false,fresh=items;if(!initial&&overlap>=0){status='OK';recovery=true;fresh=items.slice(0,overlap);}else if(errors&&!items.length){status='UNKNOWN';fresh=[];}
  const newest=items[0], newestTs=newest?.attributes?.pool_created_at?Math.floor(Date.parse(newest.attributes.pool_created_at)/1000):cp?.source_time, start=cp?.source_time??(newestTs??t);
  const ckey=await coverage(env.DB,{source,chain,eventClass:'POOL_CREATED',stream,start,end:t,status,cursorStart:cp?.cursor,cursorEnd:newest?.id||cp?.cursor,requests,r429,errors,recovery,latency:requests?latency/requests:null,pollLag:newestTs?Math.max(0,t-newestTs):null,notes:{items:items.length,fresh:fresh.length,overlap:overlap>=0}},u);
  const compact=fresh.map(it=>{const a=it.attributes||{},rels=it.relationships||{};return{id:it.id,address:a.address,created_at:a.pool_created_at,name:a.name,network:rels.network?.data?.id,dex:rels.dex?.data?.id,base:rels.base_token?.data?.id,quote:rels.quote_token?.data?.id,reserve_in_usd:a.reserve_in_usd};});
  if(compact.length){const times=compact.map(x=>Math.floor(Date.parse(x.created_at)/1000)).filter(Number.isFinite);await rawBatch(env.DB,{source,chain,eventClass:'POOL_CREATED',start:Math.min(...times),end:Math.max(...times),ingest:t,coverageKey:ckey,items:compact},u);}
  await recall(env.DB,{source,chain,stream,eventClass:'POOL_CREATED',start,end:t,count:fresh.length,success:fresh.length,coverageKey:ckey,metadata:{seen:items.length,overlap:overlap>=0}},u);
  if(newest&&(initial||recovery))await putCheckpoint(env.DB,source,chain,stream,newest.id,null,newestTs,{status},u); return {status,fresh:fresh.length,requests};
}

async function solanaRecall(env,name,program,t,u){
  const source='solana:getSignaturesForAddress',chain='solana',stream=`program:${name}:${program}`,cp=await checkpoint(env.DB,source,chain,stream,u);let rows=[],requests=0,errors=0,r429=0,latency=0,complete=false,before=null;
  try{for(let p=0;p<2;p++){const opts={limit:1000,commitment:'confirmed'};if(before)opts.before=before;if(cp?.cursor)opts.until=cp.cursor;const z=await rpc(SOLANA_RPC,'getSignaturesForAddress',[program,opts]);requests++;latency+=z.latency;const x=z.result||[];rows.push(...x);if(x.length<1000){complete=true;break;}before=x[x.length-1].signature;}}catch(e){errors++;if(e.status===429)r429++;}
  const initial=!cp,status=errors&&!rows.length?'UNKNOWN':(!complete?'PARTIAL':(initial?'PARTIAL':'OK')),newest=rows[0],newestTs=newest?.blockTime??cp?.source_time,start=cp?.source_time??(rows.length?rows[rows.length-1].blockTime:t);
  const ckey=await coverage(env.DB,{source,chain,eventClass:'PROGRAM_INTERACTION',stream,start,end:t,status,cursorStart:cp?.cursor,cursorEnd:newest?.signature||cp?.cursor,requests,r429,errors,recovery:status==='OK',latency:requests?latency/requests:null,pollLag:newestTs?Math.max(0,t-newestTs):null,notes:{program,name,raw_persisted:false}},u);
  await recall(env.DB,{source,chain,stream,eventClass:'PROGRAM_INTERACTION',start,end:t,count:rows.length,success:rows.filter(x=>!x.err).length,coverageKey:ckey,metadata:{program,name}},u);if(complete&&newest)await putCheckpoint(env.DB,source,chain,stream,newest.signature,newest.slot,newest.blockTime||t,{status},u);return{status,count:rows.length,requests};
}

async function baseFactory(env,t,u){
  const source='base:univ2_factory',chain='base',stream=`factory:${BASE_UNIV2_FACTORY.toLowerCase()}`,cp=await checkpoint(env.DB,source,chain,stream,u);let requests=0,errors=0,r429=0,latency=0,logs=[],head=0,target=0,startBlock=0,endBlock=0;
  try{let z=await rpc(BASE_RPC,'eth_blockNumber',[]);requests++;latency+=z.latency;head=hexInt(z.result);target=Math.max(0,head-2);startBlock=cp?.block_or_slot!=null?Number(cp.block_or_slot)+1:Math.max(0,target-120);endBlock=Math.min(target,startBlock+1999);if(startBlock<=endBlock){z=await rpc(BASE_RPC,'eth_getLogs',[{fromBlock:'0x'+startBlock.toString(16),toBlock:'0x'+endBlock.toString(16),address:BASE_UNIV2_FACTORY,topics:[PAIR_CREATED_TOPIC0]}]);requests++;latency+=z.latency;logs=z.result||[];}}catch(e){errors++;if(e.status===429)r429++;}
  const initial=!cp,complete=endBlock>=target&&startBlock<=endBlock,status=errors&&endBlock===0?'UNKNOWN':(initial?'PARTIAL':(complete?'OK':'PARTIAL'));let sourceTime=cp?.source_time??t;
  if(endBlock>0){try{const z=await rpc(BASE_RPC,'eth_getBlockByNumber',['0x'+endBlock.toString(16),false]);requests++;latency+=z.latency;sourceTime=hexInt(z.result?.timestamp);}catch{errors++;}}
  const start=cp?.source_time??sourceTime,ckey=await coverage(env.DB,{source,chain,eventClass:'POOL_CREATED',stream,start,end:t,status,cursorStart:cp?.cursor,cursorEnd:String(endBlock||cp?.block_or_slot||''),requests,r429,errors,recovery:status==='OK',latency:requests?latency/requests:null,pollLag:sourceTime?Math.max(0,t-sourceTime):null,notes:{factory:BASE_UNIV2_FACTORY,start_block:startBlock,end_block:endBlock,target}},u);
  const compact=[];for(const l of logs){const pool=wordAddress(l.data,0),token0=topicAddress(l.topics[1]),token1=topicAddress(l.topics[2]),b=hexInt(l.blockNumber);compact.push({id:`${l.transactionHash}:${l.logIndex}`,pool,token0,token1,block:b});}
  if(compact.length)await rawBatch(env.DB,{source,chain,eventClass:'POOL_CREATED',start,end:sourceTime,ingest:t,coverageKey:ckey,items:compact},u);
  await recall(env.DB,{source,chain,stream,eventClass:'POOL_CREATED',start,end:t,count:logs.length,success:logs.length,coverageKey:ckey,metadata:{factory:BASE_UNIV2_FACTORY}},u);if(endBlock>=startBlock&&endBlock>0)await putCheckpoint(env.DB,source,chain,stream,String(endBlock),endBlock,sourceTime,{status,target},u);return{status,count:logs.length,requests};
}

async function runCanary(env){
  const t=nowSec(),u=usage(),result={t,gecko:null,solana:{},base:null};result.gecko=await geckoScout(env,t,u);for(const[name,program]of Object.entries(SOL_PROGRAMS))result.solana[name]=await solanaRecall(env,name,program,t,u);result.base=await baseFactory(env,t,u);result.d1_usage_excluding_final_run_row={...u};await dbRun(env.DB.prepare(`INSERT INTO canary_runs(run_time,result_json) VALUES(?,?)`).bind(t,JSON.stringify(result)),u);return result;
}

export default{async scheduled(controller,env,ctx){ctx.waitUntil(runCanary(env));},async fetch(request,env){const url=new URL(request.url);if(url.pathname==='/health'){const u=usage(),rows=await dbAll(env.DB.prepare(`SELECT run_time,result_json FROM canary_runs ORDER BY run_time DESC LIMIT 1`),u);return Response.json({ok:true,last:rows[0]||null,health_read_usage:u});}return new Response('H40 GRAAC canary',{status:200});}};

"""Bounded, resumable public Bluesky Jetstream V1 intake.

Time-based microsecond cursor (legacy Jetstream hosts only). Never claim complete
coverage unless the stream actually catches up to a near-live source timestamp.
Replays are observed NOW, not retroactively first-observed at source event time.
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from urllib.parse import urlencode

PUBLIC_HOSTS = (
    "jetstream1.us-east.bsky.network",
    "jetstream2.us-west.bsky.network",
)
BASELINE_SECONDS = 16 * 60
REWIND_SECONDS = 12
MAX_LOOKBACK_SECONDS = 35 * 3600

def utc_us():
    return int(datetime.now(timezone.utc).timestamp() * 1_000_000)

def choose_start_us(prior_us, now_us):
    floor = now_us - MAX_LOOKBACK_SECONDS * 1_000_000
    if isinstance(prior_us,int) and floor <= prior_us <= now_us + 30_000_000:
        return max(floor,prior_us - REWIND_SECONDS*1_000_000), "PRIOR_CURSOR_REWIND"
    return now_us-BASELINE_SECONDS*1_000_000, "BASELINE_16M_UNKNOWN_PREHISTORY"

def event_is_near_live(ts, now_us):
    return isinstance(ts,int) and now_us-5_000_000 <= ts <= now_us+3_000_000

async def capture_events(prior_us=None,seconds=95,max_messages=80000,predicate=None):
    """Capture only filtered events in RAM, never persist unfiltered author data.
    A failover host is used ONLY for connection faults, never rate-limit response.
    """
    import websockets
    now_us=utc_us()
    cursor_us, mode=choose_start_us(prior_us,now_us)
    start_us=cursor_us
    deadline=time.monotonic()+seconds
    messages=0
    selected={}
    gap_possible=(mode!="PRIOR_CURSOR_REWIND")
    caught_up=False
    errors=[]
    active_host=None
    host_count=0
    # Stay within the same initial time cursor on failover; duplicate IDs deduped.
    for host in PUBLIC_HOSTS:
        if time.monotonic()>=deadline or messages>=max_messages:
            break
        host_count+=1
        active_host=host
        params=urlencode({"wantedCollections":"app.bsky.feed.post","cursor":str(max(start_us,cursor_us-5_000_000))})
        uri="wss://"+host+"/subscribe?"+params
        try:
            async with websockets.connect(uri,open_timeout=12,close_timeout=3,
                    ping_interval=20,ping_timeout=12,max_size=1_000_000) as ws:
                while time.monotonic()<deadline and messages<max_messages:
                    try:
                        raw=await asyncio.wait_for(ws.recv(),timeout=3)
                    except asyncio.TimeoutError:
                        continue
                    if not isinstance(raw,str):
                        continue
                    messages+=1
                    try:
                        evt=json.loads(raw)
                        ts=evt.get("time_us")
                        if isinstance(ts,int) and start_us-5_000_000<=ts<=utc_us()+3_000_000:
                            cursor_us=max(cursor_us,ts)
                            if event_is_near_live(ts,utc_us()):
                                caught_up=True
                        if predicate is not None and predicate(evt):
                            k=str(evt.get("did") or "")+":"+str((evt.get("commit") or {}).get("rkey") or "")
                            if k!=":" and len(selected)<800:
                                selected[k]=evt
                    except (ValueError,TypeError,AttributeError):
                        continue
                    if caught_up and time.monotonic()+3<deadline:
                        # Capture a further short live slice, not another whole backlog.
                        live_until=time.monotonic()+3
                        while time.monotonic()<live_until:
                            try: 
                                rr=await asyncio.wait_for(ws.recv(),timeout=1)
                                ev=json.loads(rr)
                                messages+=1
                                ts=ev.get("time_us")
                                if isinstance(ts,int) and ts<=utc_us()+3_000_000:
                                    cursor_us=max(cursor_us,ts)
                                if predicate is not None and predicate(ev):
                                    k=str(ev.get("did") or "")+":"+str((ev.get("commit") or {}).get("rkey") or "")
                                    if k!=":" and len(selected)<800:
                                        selected[k]=ev
                            except asyncio.TimeoutError:
                                continue
                            except (ValueError,TypeError,AttributeError):
                                continue
                    if caught_up:
                        break
                # No failover for a healthy connection that simply hit a time/message cap.
                break
        except websockets.exceptions.InvalidStatus as exc:
            status=getattr(getattr(exc,"response",None),"status_code",None)
            errors.append({"kind":"WEBSOCKET_HTTP_STATUS","status":status,"host":host})
            if status in (401,403,429):
                break   # Never switch instances to evade access/rate limits.
            continue
        except (OSError,TimeoutError,asyncio.TimeoutError,websockets.exceptions.ConnectionClosed) as exc:
            errors.append({"kind":type(exc).__name__,"host":host})
            continue
    health={
        "surface":"bluesky:jetstream_crypto",
        "ok":host_count>0 and (messages>0 or caught_up),
        "transport":"OFFICIAL_PUBLIC_LEGACY_JETSTREAM_V1",
        "host":active_host,
        "start_mode":mode,
        "messages_seen":messages,
        "filtered_posts":len(selected),
        "cursor_start_us":start_us,
        "cursor_end_us":cursor_us if messages else None,
        "caught_up_near_live":caught_up,
        "coverage_status":"COVERED_REPLAY_TO_LIVE" if caught_up and not gap_possible else "PARTIAL_OR_BASELINE_UNKNOWN",
        "time_limit_s":seconds,
        "errors":errors[:2],
        "replayed_without_retroactive_freeze":True
    }
    return list(selected.values()),health,cursor_us if messages else prior_us

def offline_test():
    nowus=utc_us()
    v,mode=choose_start_us(nowus-14*60*1_000_000,nowus)
    assert mode=="PRIOR_CURSOR_REWIND" and v < nowus-14*60*1_000_000
    v,mode=choose_start_us(None,nowus)
    assert mode.startswith("BASELINE") and v==nowus-BASELINE_SECONDS*1_000_000
    assert event_is_near_live(nowus-1_000_000,nowus)
    assert not event_is_near_live(nowus-16*60*1_000_000,nowus)
    print("PASS: Jetstream time-cursor v1 replay, rewind, honest baseline coverage")

"""Approved OAuth-based Reddit coverage for FEE100K. Disabled without explicit access setup.

No proxy rotation or anonymous retry on 401/403/429. Never store an API token in
GitHub artifacts or Supabase. Caller supplies a converter for JSON Reddit posts.
"""
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

API_BASE="https://oauth.reddit.com"
TOKEN_URL="https://www.reddit.com/api/v1/access_token"

class RedditAccessError(Exception):
    def __init__(self,kind,http_status=None,retry_after=None):
        self.kind=kind
        self.http_status=http_status
        self.retry_after=retry_after
        super().__init__(kind)

def setup():
    approved=os.getenv("REDDIT_ACCESS_APPROVED","").strip().lower()=="true"
    app_id=os.getenv("REDDIT_CLIENT_ID","").strip()
    app_secret=os.getenv("REDDIT_CLIENT_SECRET","").strip()
    user_agent=os.getenv("REDDIT_USER_AGENT","").strip()
    if not approved:
        return None,"REDDIT_EXPLICIT_APPROVAL_REQUIRED"
    if not app_id or not app_secret or not user_agent:
        return None,"REDDIT_OAUTH_SECRETS_OR_UA_MISSING"
    if len(user_agent)>200 or "by " not in user_agent.lower():
        return None,"REDDIT_VALID_TRANSPARENT_UA_REQUIRED"
    return {"id":app_id,"secret":app_secret,"ua":user_agent},None

def get_token(config,timeout=12):
    auth=base64.b64encode((config["id"]+":"+config["secret"]).encode()).decode()
    data=urllib.parse.urlencode({"grant_type":"client_credentials"}).encode()
    req=urllib.request.Request(TOKEN_URL,data=data,headers={
        "Authorization":"Basic "+auth,
        "User-Agent":config["ua"],
        "Content-Type":"application/x-www-form-urlencoded",
        "Accept":"application/json",
    })
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            payload=json.loads(r.read(128_000))
        token=payload.get("access_token")
        if not token:
            raise RedditAccessError("REDDIT_OAUTH_TOKEN_MISSING")
        return token
    except urllib.error.HTTPError as exc:
        raise RedditAccessError("REDDIT_OAUTH_HTTP",exc.code,exc.headers.get("Retry-After")) from None

def fetch_feed(config, token, subreddit, feed="new",timeout=12):
    path="/r/"+urllib.parse.quote(subreddit,safe="")+"/"+feed
    url=API_BASE+path+"?limit=25"
    req=urllib.request.Request(url,headers={
        "Authorization":"bearer "+token,
        "User-Agent":config["ua"],
        "Accept":"application/json",
    })
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            raw=r.read(1_000_001)
        if len(raw)>1_000_000:
            raise RedditAccessError("REDDIT_FEED_OVER_1MB")
        p=json.loads(raw)
        children=((p.get("data") or {}).get("children") or [])
        return [x.get("data") for x in children if x.get("kind")=="t3" and isinstance(x.get("data"),dict)][:25]
    except urllib.error.HTTPError as exc:
        raise RedditAccessError("REDDIT_FEED_HTTP",exc.code,exc.headers.get("Retry-After")) from None

def offline_test():
    import unittest.mock
    with unittest.mock.patch.dict(os.environ,{"REDDIT_ACCESS_APPROVED":"false"},clear=True):
        c,reason=setup()
        assert c is None and reason=="REDDIT_EXPLICIT_APPROVAL_REQUIRED"
    with unittest.mock.patch.dict(os.environ,{
       "REDDIT_ACCESS_APPROVED":"true","REDDIT_CLIENT_ID":"id","REDDIT_CLIENT_SECRET":"secret",
       "REDDIT_USER_AGENT":"app:FEE100K:1 (by u/approved_operator)"
    },clear=True):
        c,reason=setup()
        assert c is not None and not reason
    print("PASS: Reddit OAuth explicitly gated; no anonymous 403/429 retry")

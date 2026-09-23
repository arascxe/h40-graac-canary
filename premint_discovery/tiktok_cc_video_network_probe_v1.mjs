import { chromium } from "playwright";
const browser = await chromium.launch({headless:true,args:["--disable-dev-shm-usage","--no-sandbox"]});
const data = {schema:"tiktok_video_network_diagnostic_v1",ok:false,network:[],dom:{},errors:[]};
function shape(v,level=0) {
  if(level>3 || v===null)return typeof v;
  if(Array.isArray(v))return {kind:"array",length:v.length,first:v.length?shape(v[0],level+1):null};
  if(typeof v==="object")return {kind:"object",keys:Object.keys(v).slice(0,24),
    children:Object.fromEntries(Object.entries(v).filter(([k,val])=> val&&typeof val==="object").slice(0,6).map(([k,val])=>[k,shape(val,level+1)]))};
  return typeof v;
}
try{
  const context=await browser.newContext({viewport:{width:1365,height:900},userAgent:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"});
  const page=await context.newPage();
  page.on("response",async resp=>{
    let u;try{u=new URL(resp.url());}catch{return;}
    if(!/(cc_portal_api|creative_radar_api|\/api\/trends|\/video)/i.test(u.pathname))return;
    if(data.network.length>=35)return;
    const ev={host:u.hostname,path:u.pathname,status:resp.status(),contentType:resp.headers()["content-type"]?.split(";")[0]};
    if(ev.contentType?.includes("json")){
      try{const obj=await resp.json();ev.shape=shape(obj);ev.code=obj?.code??null;}catch(e){ev.parseError=String(e).slice(0,80);}
    }
    data.network.push(ev);
  });
  const url="https://ads.tiktok.com/creative/creativeCenter/trends/video?region=US&period=7";
  const response=await page.goto(url,{waitUntil:"domcontentloaded",timeout:60000});
  data.ok=Boolean(response?.ok());
  await page.waitForTimeout(16000);
  await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight)).catch(()=>{});
  await page.waitForTimeout(4000);
  data.dom=await page.evaluate(()=>{
    const links=Array.from(document.querySelectorAll("a[href]")).map(a=>a.href);
    const imageUrls=Array.from(document.querySelectorAll("img")).map(x=>x.src);
    const scripts=Array.from(document.querySelectorAll("script")).map(x=>({id:x.id,type:x.type,len:x.textContent?.length||0}));
    return {title:document.title,bodySample:(document.body.innerText||"").replace(/\\s+/g," ").slice(0,1000),
      anchorCount:links.length,videoAnchorCount:links.filter(u=>u.includes("/video/")).length,
      anchorHosts:Array.from(new Set(links.map(u=>{try{return new URL(u).hostname;}catch{return "";}}))).slice(0,15),
      imageCount:imageUrls.length,imageHosts:Array.from(new Set(imageUrls.map(u=>{try{return new URL(u).hostname;}catch{return "";}}))).slice(0,10),
      scriptMeta:scripts.filter(x=>x.id||x.len>40000).slice(0,12)};
  });
  await context.close();
}catch(e){data.errors.push(String(e?.message||e).slice(0,200));}
finally{await browser.close();}
console.log(JSON.stringify(data));

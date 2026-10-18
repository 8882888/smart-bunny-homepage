(function(root){
  "use strict";
  const input=typeof module!=="undefined"&&module.exports?require('./trip-input.js'):root.SmartBunnyTripInput;
  const LIMIT=40;
  function normalizeRows(rows){
    if(!Array.isArray(rows))return [];
    return rows.flatMap(row=>{
      if(!row||typeof row!=="object")return [];
      const date=String(row['운행일']||'');
      const time=String(row['출발 시간']||row['출발시간']||'');
      const origin=row['출발지'],destination=row['도착지'],amount=Number(row['금액']);
      try{input.validateTrip({trip_date:date,departure_time:time,origin,destination,fare_krw:amount,service_type:'daeri',status:'completed'});}catch(error){return [];}
      if(/자택|집앞|일일\s*기사|건당\s*[xX×]|고정\s*[-:.：]|대기\s*기사|지인\s*빌딩\s*뒤/.test(origin+' '+destination))return [];
      // Return only these five public fields; never pass through arbitrary DB keys.
      return [{'운행일':date,'출발 시간':time,'출발지':origin,'도착지':destination,'금액':amount}];
    }).sort((a,b)=>(b['운행일']+' '+b['출발 시간']).localeCompare(a['운행일']+' '+a['출발 시간'])).slice(0,LIMIT);
  }
  async function getJSON(url,headers,fetcher,timeoutMs){
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),timeoutMs);
    try{
      const response=await fetcher(url,{headers,signal:controller.signal,cache:'no-store'});
      if(!response.ok)throw new Error('Public review request failed');
      return await response.json();
    }finally{clearTimeout(timeout);}
  }
  async function load(options={}){
    const fetcher=options.fetcher||root.fetch.bind(root);
    const config=options.config;
    const timeoutMs=options.timeoutMs||5000;
    if(config&&config.url&&config.anonKey){
      try{
        const params=new URLSearchParams({select:'"운행일","출발 시간","출발지","도착지","금액"',order:'운행일.desc,출발 시간.desc',limit:String(LIMIT)});
        const raw=await getJSON(config.url.replace(/\/$/,'')+'/rest/v1/completed_trip_reviews?'+params,{'apikey':config.anonKey,'Accept':'application/json'},fetcher,timeoutMs);
        const rows=normalizeRows(raw);
        if(rows.length)return {rows,source:'live',total:null};
      }catch(error){/* Preserve published records when the public view is unavailable. */}
    }
    const data=await getJSON(options.fallbackURL||'./data/latest_public_trips.json',{},fetcher,timeoutMs);
    const rows=normalizeRows(data.trips);
    return {rows,source:'published',total:Number.isInteger(data.total)&&data.total>=rows.length?data.total:rows.length};
  }
  const api={load,normalizeRows};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  else root.SmartBunnyPublicReviews=api;
})(typeof window!=="undefined"?window:globalThis);

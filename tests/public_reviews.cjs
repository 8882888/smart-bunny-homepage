const assert=require('node:assert/strict');
const fs=require('node:fs');
const {load,normalizeRows}=require('../public-reviews.js');
const row={'운행일':'2026-10-19','출발 시간':'09:30','출발지':'서울 강남구','도착지':'부산 동래구','금액':120000};
const response=data=>({ok:true,json:async()=>data});
const config={url:'https://example.test',anonKey:'public-test-key'};
(async()=>{
  let calls=[];
  const live=await load({config,fetcher:async(url,options)=>{calls.push({url,options});return response([{...row,customer_name:'not-a-public-field'}]);}});
  assert.equal(live.source,'live');assert.equal(calls.length,1);
  assert.equal(new URL(calls[0].url).pathname,'/rest/v1/completed_trip_reviews');
  assert.equal(new URL(calls[0].url).searchParams.get('limit'),'40');
  assert.equal(calls[0].options.headers.apikey,config.anonKey);
  assert.deepEqual(Object.keys(live.rows[0]).sort(),Object.keys(row).sort());
  for(const liveData of [[],[{...row,'출발지':'010-1234-5678'}]]){
    calls=[];const data=await load({config,fetcher:async url=>{calls.push(url);return response(calls.length===1?liveData:{total:2522,trips:[row]});}});
    assert.equal(data.source,'published');assert.equal(data.total,2522);assert.equal(data.rows.length,1);assert.equal(calls.length,2);
  }
  let count=0;const failed=await load({config,fetcher:async()=>{if(++count===1)throw Error('offline');return response({total:1,trips:[row]});}});assert.equal(failed.source,'published');
  let aborted=false;const timed=await load({config,timeoutMs:5,fetcher:async(url,options)=>{
    if(url.includes('/rest/'))return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>{aborted=true;reject(new Error('timeout'));}));
    return response({total:1,trips:[row]});
  }});assert.equal(aborted,true);assert.equal(timed.rows.length,1);
  assert.equal(normalizeRows(Array.from({length:100},()=>row)).length,40);
  assert.equal(normalizeRows([{...row,'運行日':'x','운행일':'2026-02-30'},{...row,'도착지':'콜센터 확인'},{...row,'금액':-1}]).length,0);
  const feed=JSON.parse(fs.readFileSync('data/latest_public_trips.json','utf8'));
  assert(feed.trips.length<=40);assert.equal(normalizeRows(feed.trips).length,feed.trips.length);
  assert(!fs.readFileSync('index.html','utf8').includes('fetch("./reviews/"'));
  const markup=fs.readFileSync('reviews/index.html','utf8');
  const start=markup.indexOf('function filterTripRows(query)');
  const end=markup.indexOf('tripSearch.addEventListener',start);
  const records=[['2026-10-19','09:30','서울 강남구','부산 동래구','120,000원'],['2026-10-18','10:00','인천','대구','100,000원']].map(cells=>({cells:cells.map(textContent=>({textContent})),classList:{toggle(name,hidden){this.hidden=hidden;}}}));
  const searchCount={};
  require('node:vm').runInNewContext(markup.slice(start,end)+';filterTripRows("서울 강남구 부산 동래구");',{document:{querySelectorAll:()=>records},searchCount});
  assert.equal(records[0].classList.hidden,false);assert.equal(records[1].classList.hidden,true);assert.equal(searchCount.textContent,'검색 결과 1건');
  console.log('PASS: live public view, published fallback, timeout, five-field privacy filter, record limit and generated feed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

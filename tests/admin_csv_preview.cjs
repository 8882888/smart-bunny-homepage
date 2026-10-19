const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('admin/index.html','utf8');
const start=html.indexOf(' function clearCSVPreview()'),end=html.indexOf(' client.auth.onAuthStateChange',start);
const nodes={};const $=id=>nodes[id]||=({value:'',listeners:{},disabled:false,classList:{hidden:true,add(){this.hidden=true},remove(){this.hidden=false}},addEventListener(name,fn){this.listeners[name]=fn}});
let content='서비스구분,운행일,출발시간,출발지,도착지,금액\n탁송,2026-10-19,09:30,서울,부산,120000';
let writes=0,status='',fail=false,accept=true;
$('csv-file').files=[{text:async()=>content}];
const client={from(){return this},async insert(){writes++;return {error:fail?new Error('mock failure'):null}}};
vm.runInNewContext('let pendingCSVRows=[],csvBusy=false;'+html.slice(start,end),{$,window:{SmartBunnyTripInput:require('../trip-input.js')},client,confirm:()=>accept,statusText:s=>{status=s},loadRecords:async()=>{},escapeHtml:s=>String(s).replace(/</g,'&lt;'),money:n=>n+'원'});
(async()=>{
 await $('csv-import').listeners.click();assert.equal(writes,0);assert.equal($('csv-preview-panel').classList.hidden,false);assert($('csv-preview-table').innerHTML.includes('서울'));assert(status.includes('아직 저장하지'));
 $('csv-cancel').listeners.click();await $('csv-confirm').listeners.click();assert.equal(writes,0);
 await $('csv-import').listeners.click();accept=false;await $('csv-confirm').listeners.click();assert.equal(writes,0);accept=true;
 await Promise.all([$('csv-confirm').listeners.click(),$('csv-confirm').listeners.click()]);assert.equal(writes,1);assert.equal($('csv-confirm').disabled,false);assert.equal($('csv-preview-panel').classList.hidden,true);
 content='서비스구분,운행일,출발시간,출발지,도착지,금액\n탁송';await $('csv-import').listeners.click();await $('csv-confirm').listeners.click();assert.equal(writes,1);assert(status.includes('미리보기 중단'));
 content='서비스구분,운행일,출발시간,출발지,도착지,금액\n탁송,2026-10-19,09:30,서울,부산,120000';await $('csv-import').listeners.click();fail=true;await $('csv-confirm').listeners.click();assert(status.includes('등록 오류'));assert.equal($('csv-import').disabled,false);await $('csv-confirm').listeners.click();assert.equal(writes,2,'failed batch must not be blindly retried');
 console.log('PASS: preview never saves; cancel, invalid CSV, declined confirmation and double clicks do not insert; errors reset controls.');
})().catch(error=>{console.error(error);process.exitCode=1});

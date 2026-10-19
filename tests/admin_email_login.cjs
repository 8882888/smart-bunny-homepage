const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('admin/index.html','utf8');
assert(!html.includes('type="password"'));assert(!html.includes('signInWithPassword'));assert(html.includes('role!=="admin"'));assert(html.includes('client.auth.signOut()'));
const nodes={};const $=id=>nodes[id]||=({value:'',disabled:false,textContent:'',addEventListener(name,fn){this[name]=fn}});
let calls=[],fail=false,release;
const client={auth:{async signInWithOtp(args){calls.push(args);await new Promise(r=>release=r);return {error:fail?{message:'mail unavailable'}:null}}}};
const start=html.indexOf(' let loginBusy='),end=html.indexOf(' $("logout")',start);
vm.runInNewContext(html.slice(start,end),{$,client,URL,location:{href:'https://8882888.github.io/smart-bunny-homepage/admin/'},statusText:(s,id)=>$(id).textContent=s,Date});
(async()=>{
 $('email').value=' admin@example.com ';
 const event={preventDefault(){}};
 const pending=$('login-form').submit(event);await $('login-form').submit(event);assert.equal(calls.length,1);assert.equal($('send-login-link').disabled,true);
 assert.equal(calls[0].email,'admin@example.com');assert.equal(calls[0].options.shouldCreateUser,false);assert.equal(calls[0].options.emailRedirectTo,'https://8882888.github.io/smart-bunny-homepage/admin/');
 fail=true;release();await pending;assert($('login-status').textContent.includes('mail unavailable'));assert.equal($('send-login-link').disabled,false);
 fail=false;const next=$('login-form').submit(event);release();await next;await $('login-form').submit(event);assert.equal(calls.length,2);assert($('login-status').textContent.includes('잠시 후'));
 console.log('PASS: passwordless request, no signup, canonical callback, duplicate/cooldown and failure handling; admin role guard retained.');
})().catch(e=>{console.error(e);process.exitCode=1});

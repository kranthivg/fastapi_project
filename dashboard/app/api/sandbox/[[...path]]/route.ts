import { env } from 'cloudflare:workers';
export const dynamic = 'force-dynamic';
const people = [{id:1,email:'author@example.com'},{id:2,email:'reader@example.com'}];
const json=(data:unknown,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store'}});
async function handle(req:Request){
 const workspace=req.headers.get('oai-authenticated-user-id');
 if(!workspace)return json({detail:'Sign in to open your private sandbox'},401);
 const db=env.DB;if(!db)return json({detail:'Database unavailable'},503);
 const uid=Number(req.headers.get('x-persona')||1);if(![1,2].includes(uid))return json({detail:'Unknown sandbox persona'},422);
 const url=new URL(req.url),path=url.pathname.replace('/api/sandbox','').replace(/\/$/,'')||'/',method=req.method;
 const query=(sql:string,...args:any[])=>db.prepare(sql).bind(...args);
 const shape=(p:any)=>({Post:{id:p.id,title:p.title,content:p.content,published:!!p.published,owner_id:p.owner_id,created:p.created,owner:{...people[p.owner_id-1],created:p.created}},votes:Number(p.votes||0),voted:!!p.voted});
 try{
 if(path==='/health')return json({status:'ok',runtime:'Sites Worker + D1',mode:'sandbox'});
 if(path==='/users/me')return json({...people[uid-1],created:new Date().toISOString()});
 if(path==='/posts'&&method==='GET'){
  const limit=Number(url.searchParams.get('limit')||20),skip=Number(url.searchParams.get('skip')||0),search=url.searchParams.get('search')||'';
  if(!Number.isInteger(limit)||limit<1||limit>100||!Number.isInteger(skip)||skip<0||search.length>200)return json({detail:'Invalid pagination or search'},422);
  const result=await query(`SELECT p.*, (SELECT COUNT(*) FROM studio_votes v WHERE v.post_id=p.id AND v.workspace=p.workspace) votes, (SELECT COUNT(*) FROM studio_votes v WHERE v.post_id=p.id AND v.workspace=p.workspace AND v.user_id=?) voted FROM studio_posts p WHERE p.workspace=? AND (p.published=1 OR p.owner_id=?) AND instr(lower(p.title),lower(?))>0 ${url.searchParams.get('mine')==='true'?'AND p.owner_id='+uid:''} ORDER BY p.id DESC LIMIT ? OFFSET ?`,uid,workspace,uid,search,limit,skip).all();return json(result.results.map(shape));
 }
 let body:any={};if(['POST','PUT'].includes(method)){const raw=await req.text();if(raw.length>25000)return json({detail:'Body too large'},413);try{body=JSON.parse(raw)}catch{return json({detail:'Invalid JSON'},422)}}
 const id=Number(path.split('/')[2]);
 if(path==='/posts'&&method==='POST'||path.startsWith('/posts/')&&method==='PUT'){
  if(typeof body.title!=='string'||!body.title.trim()||body.title.trim().length>200||typeof body.content!=='string'||!body.content.trim()||body.content.length>20000||body.published!==undefined&&typeof body.published!=='boolean')return json({detail:'Title (1–200), content (1–20,000), and a boolean published value are required'},422);
  let pid=id;
  if(method==='PUT'){const found=await query('SELECT * FROM studio_posts WHERE id=? AND workspace=?',id,workspace).first<any>();if(!found)return json({detail:'Post not found'},404);if(found.owner_id!==uid)return json({detail:'Only the author can change this post'},403);await query('UPDATE studio_posts SET title=?,content=?,published=? WHERE id=? AND workspace=?',body.title.trim(),body.content.trim(),body.published===false?0:1,id,workspace).run()}
  else {const inserted=await query('INSERT INTO studio_posts(workspace,owner_id,title,content,published) VALUES (?,?,?,?,?)',workspace,uid,body.title.trim(),body.content.trim(),body.published===false?0:1).run();pid=Number(inserted.meta.last_row_id)}
  return json(shape(await query('SELECT * FROM studio_posts WHERE id=? AND workspace=?',pid,workspace).first()).Post,method==='POST'?201:200);
 }
 if(path.startsWith('/posts/')&&['GET','DELETE'].includes(method)){
  const p=await query('SELECT p.*,(SELECT COUNT(*) FROM studio_votes v WHERE v.post_id=p.id AND v.workspace=p.workspace) votes,(SELECT COUNT(*) FROM studio_votes v WHERE v.post_id=p.id AND v.workspace=p.workspace AND v.user_id=?) voted FROM studio_posts p WHERE p.id=? AND p.workspace=?',uid,id,workspace).first<any>();
  if(!p||!p.published&&p.owner_id!==uid)return json({detail:'Post not found'},404);
  if(method==='GET')return json(shape(p));if(p.owner_id!==uid)return json({detail:'Only the author can delete this post'},403);
  await query('DELETE FROM studio_posts WHERE id=? AND workspace=?',id,workspace).run();return new Response(null,{status:204});
 }
 if(path==='/vote'&&method==='POST'){
  if(!Number.isInteger(body.post_id)||body.post_id<1||![0,1].includes(body.dir))return json({detail:'post_id must be positive and dir must be 0 or 1'},422);
  const p=await query('SELECT * FROM studio_posts WHERE id=? AND workspace=?',body.post_id,workspace).first<any>();if(!p||!p.published&&p.owner_id!==uid)return json({detail:'Post not found'},404);
  if(body.dir===1){const r=await query('INSERT OR IGNORE INTO studio_votes(workspace,user_id,post_id) VALUES(?,?,?)',workspace,uid,body.post_id).run();if(!r.meta.changes)return json({detail:'Already voted'},409)}else{const r=await query('DELETE FROM studio_votes WHERE workspace=? AND user_id=? AND post_id=?',workspace,uid,body.post_id).run();if(!r.meta.changes)return json({detail:'Vote does not exist'},404)}return json({message:body.dir===1?'Successfully added vote':'Successfully deleted vote'},201);
 }
 return json({detail:'Endpoint not found'},404);
 }catch(e){console.error('Sandbox request failed',e);return json({detail:'Request failed. Please retry.'},500)}
}
export {handle as GET,handle as POST,handle as PUT,handle as DELETE};

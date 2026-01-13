const BACKEND_URL="https://YOUR-BACKEND-URL";
const sessionId = crypto.randomUUID();

const chat=document.getElementById("chat");
const input=document.getElementById("input");
const sendBtn=document.getElementById("sendBtn");
const lang=document.getElementById("language");
const sourcesList=document.getElementById("sourcesList");

function add(role,text){
  const d=document.createElement("div");
  d.className="msg "+role;
  const b=document.createElement("div");
  b.className="bubble";
  b.textContent=text;
  d.appendChild(b);
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
  return b;
}

function setSources(s){
  sourcesList.innerHTML="";
  (s||[]).forEach((x,i)=>{
    const li=document.createElement("li");
    li.textContent=`[${i+1}] ${x.title} — ${x.source}`;
    sourcesList.appendChild(li);
  });
}

function parse(buf){
  let out=[],i;
  while((i=buf.indexOf("\n\n"))!=-1){
    const raw=buf.slice(0,i);buf=buf.slice(i+2);
    let ev="message",data=[];
    raw.split("\n").forEach(l=>{
      if(l.startsWith("event:"))ev=l.slice(6).trim();
      if(l.startsWith("data:"))data.push(l.slice(5).trim());
    });
    out.push({event:ev,data:data.join("\n").replace(/\\n/g,"\n")});
  }
  return {out,buf};
}

async function send(){
  const text=input.value.trim();
  if(!text)return;
  input.value="";
  setSources([]);
  add("user",text);
  const a=add("assistant","");

  const res=await fetch(BACKEND_URL+"/chat/stream",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({message:text,session_id:sessionId,language:lang.value})
  });

  const r=res.body.getReader();
  const dec=new TextDecoder();
  let buf="";
  while(true){
    const {value,done}=await r.read();
    if(done)break;
    buf+=dec.decode(value,{stream:true});
    const p=parse(buf);buf=p.buf;
    p.out.forEach(e=>{
      if(e.event==="meta")setSources(JSON.parse(e.data).sources);
      if(e.event==="token")a.textContent+=e.data;
    });
  }
}

sendBtn.onclick=send;
input.onkeydown=e=>{if(e.key==="Enter")send();}

add("assistant","Hi! Ask me about UK attractions, festivals, seasons, or transport.");

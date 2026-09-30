(function(){
'use strict';
const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const canvas=$('#ntsCanvas'), linksSvg=$('#ntsLinks'), empty=$('#ntsEmpty'), prompt=$('#ntsPrompt');
if(!canvas)return;

const icons={cloud:'bi-cloud',router:'bi-router',firewall:'bi-shield-lock',switch:'bi-diagram-3',olt:'bi-hdd-network',server:'bi-server',ap:'bi-wifi',client:'bi-pc-display'};
const labels={cloud:'ISP',router:'Router',firewall:'Firewall',switch:'Switch',olt:'OLT',server:'Server',ap:'Wi-Fi AP',client:'Client'};
let topology={nodes:[],links:[],vlans:[]}, selectedId=null, eventCount=0, failure=null;

function uid(prefix){return prefix+'-'+Math.random().toString(36).slice(2,8)}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function log(message,type='INFO'){
  eventCount+=1; const host=$('#ntsEvents');
  if(eventCount===1)host.innerHTML='';
  const p=document.createElement('p');p.innerHTML='<time>'+type+'</time>'+escapeHtml(message);host.prepend(p);
}
function count(text,patterns,fallback=0){
  const lower=text.toLowerCase();
  for(const [words,value] of patterns){if(words.some(w=>lower.includes(w)))return value}
  return fallback;
}
function wordNumber(text,before){
  const lower=text.toLowerCase();
  const nums={one:1,two:2,three:3,four:4,five:5,six:6,eight:8,একটি:1,একটা:1,দুইটি:2,দুটি:2,তিনটি:3,চারটি:4,পাঁচটি:5,ছয়টি:6};
  const keys=Object.keys(nums).join('|');
  const match=lower.match(new RegExp('(?:'+keys+'|\\d+)\\s+(?:redundant\\s+)?(?:'+before+')'));
  if(!match)return 0; const token=match[0].split(/\s+/)[0];return Number(token)||nums[token]||0;
}
function makeNode(type,name,level,index,total,vendor='Generic'){
  const width=Math.max(canvas.clientWidth,280),height=Math.max(canvas.clientHeight,500);
  const x=((index+1)/(total+1))*Math.max(width-140,140); const y=58+level*Math.min(135,(height-130)/4);
  return{id:uid(type),type,name,vendor,ip:'',x:Math.round(x),y:Math.round(y),level};
}
function parsePrompt(text){
  const lower=text.toLowerCase();
  const ispCount=Math.max(wordNumber(text,'isp|upstream|provider'),/(two|দুইটি|দুটি).*?(isp|upstream|provider)/i.test(text)?2:1);
  const routerCount=Math.max(wordNumber(text,'router|edge router|mikrotik'),lower.includes('router')||lower.includes('mikrotik')?1:0);
  const firewallCount=Math.max(wordNumber(text,'firewall'),lower.includes('firewall')?1:0);
  const coreCount=Math.max(wordNumber(text,'core switch|core'),lower.includes('core')?(/redundant|dual|দুইটি|দুটি/.test(lower)?2:1):0);
  const accessCount=Math.max(wordNumber(text,'access switch|access switches'),lower.includes('access switch')?1:0);
  const oltCount=Math.max(wordNumber(text,'olt|olts'),lower.includes('olt')?1:0);
  const serverCount=Math.max(wordNumber(text,'server|servers'),lower.includes('server')?1:0);
  const apCount=Math.max(wordNumber(text,'wireless access point|access points|wifi ap|wi-fi ap'),/(wireless|wi-fi|wifi).*(access point|ap)/.test(lower)?1:0);
  const vlans=Array.from(text.matchAll(/vlan\s*(\d+)/gi)).map(m=>Number(m[1])).filter((v,i,a)=>a.indexOf(v)===i);
  const nodes=[],groups={cloud:[],edge:[],core:[],access:[],endpoint:[]};
  function add(type,n,level,prefix,vendor){for(let i=0;i<n;i++){const node=makeNode(type,prefix+(n>1?' '+(i+1):''),level,i,n,vendor);nodes.push(node);groups[level===0?'cloud':level===1?'edge':level===2?'core':level===3?'access':'endpoint'].push(node)}}
  add('cloud',ispCount,0,'ISP');
  if(routerCount)add('router',routerCount,1,lower.includes('mikrotik')?'MikroTik Edge':'Edge Router',lower.includes('mikrotik')?'MikroTik':'Generic');
  if(firewallCount)add('firewall',firewallCount,1,'Firewall');
  if(!routerCount&&!firewallCount)add('router',1,1,'Edge Router');
  add('switch',coreCount||1,2,'Core Switch');
  add('switch',accessCount,3,'Access Switch');
  add('olt',oltCount,3,'OLT','Huawei');
  add('server',serverCount,4,'Server');
  add('ap',apCount,4,'Access Point');
  const links=[];function connect(a,b,label){if(a&&b)links.push({id:uid('link'),from:a.id,to:b.id,label,status:'healthy'})}
  const edge=groups.edge.length?groups.edge:[nodes.find(n=>n.level===1)];
  groups.cloud.forEach((n,i)=>connect(n,edge[i%edge.length],i===0?'Primary WAN':'Backup WAN'));
  edge.forEach(n=>groups.core.forEach(c=>connect(n,c,'Uplink')));
  const distribution=groups.access.length?groups.access:groups.endpoint.filter(n=>n.type==='olt');
  distribution.forEach((n,i)=>connect(groups.core[i%groups.core.length],n,n.type==='olt'?'PON Uplink':'Trunk'));
  groups.endpoint.filter(n=>n.type!=='olt').forEach((n,i)=>connect((distribution[i%distribution.length]||groups.core[i%groups.core.length]),n,'LAN'));
  if(groups.core.length>1)connect(groups.core[0],groups.core[1],'Core Peer');
  return{nodes,links,vlans};
}
function autoLayout(announce=true){
  const width=Math.max(canvas.clientWidth,280),nodeWidth=width<520?112:126;
  const levels={};topology.nodes.forEach(n=>(levels[n.level]||(levels[n.level]=[])).push(n));
  let cursorY=38;
  Object.keys(levels).sort((a,b)=>Number(a)-Number(b)).forEach(level=>{
    const nodes=levels[level],columns=width<520?Math.min(2,nodes.length):nodes.length;
    const rows=Math.ceil(nodes.length/Math.max(columns,1));
    nodes.forEach((n,i)=>{
      const row=Math.floor(i/columns),column=i%columns,itemsInRow=Math.min(columns,nodes.length-row*columns);
      const slot=width/itemsInRow;
      n.x=Math.max(6,Math.round(column*slot+(slot-nodeWidth)/2));
      n.y=cursorY+row*92;
    });
    cursorY+=rows*92+24;
  });
  canvas.style.minHeight=Math.max(500,cursorY+30)+'px';
  render();if(announce)log('Topology arranged into logical network layers.','LAYOUT');
}
function render(){
  canvas.querySelectorAll('.nts-node').forEach(n=>n.remove());empty.hidden=topology.nodes.length>0;
  topology.nodes.forEach(node=>{
    const el=document.createElement('button');el.type='button';el.className='nts-node'+(node.id===selectedId?' selected':'')+(node.failed?' failed':'');
    el.dataset.id=node.id;el.style.left=node.x+'px';el.style.top=node.y+'px';
    el.innerHTML='<span class="nts-node-head"><span class="nts-node-icon"><i class="bi '+icons[node.type]+'"></i></span><span><strong>'+escapeHtml(node.name)+'</strong><small>'+escapeHtml(node.vendor||'Generic')+' · '+escapeHtml(labels[node.type])+'</small></span></span><span class="nts-node-port"><span>'+escapeHtml(node.ip||'No IP')+'</span><i class="bi bi-grip-horizontal"></i></span>';
    el.addEventListener('click',()=>selectNode(node.id));enableDrag(el,node);canvas.appendChild(el);
  });drawLinks();updateSummary();updateInspector();
}
function drawLinks(){
  linksSvg.innerHTML='<defs><marker id="ntsArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#22d3ee"/></marker></defs>';
  const ns='http://www.w3.org/2000/svg';
  topology.links.forEach(link=>{
    const a=topology.nodes.find(n=>n.id===link.from),b=topology.nodes.find(n=>n.id===link.to);if(!a||!b)return;
    const x1=a.x+63,y1=a.y+36,x2=b.x+63,y2=b.y+36;
    const path=document.createElementNS(ns,'path');path.setAttribute('d',`M ${x1} ${y1} C ${x1} ${(y1+y2)/2}, ${x2} ${(y1+y2)/2}, ${x2} ${y2}`);path.setAttribute('class','nts-link '+(link.status||''));if(link.status==='active')path.setAttribute('marker-end','url(#ntsArrow)');linksSvg.appendChild(path);
    const label=document.createElementNS(ns,'text');label.setAttribute('x',(x1+x2)/2);label.setAttribute('y',(y1+y2)/2-5);label.setAttribute('text-anchor','middle');label.setAttribute('class','nts-link-label');label.textContent=link.label||'';linksSvg.appendChild(label);
  });
}
function enableDrag(el,node){
  el.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;el.setPointerCapture(e.pointerId);const sx=e.clientX,sy=e.clientY,ox=node.x,oy=node.y;
    const move=ev=>{node.x=Math.max(0,Math.min(canvas.clientWidth-126,ox+ev.clientX-sx));node.y=Math.max(0,Math.min(canvas.clientHeight-72,oy+ev.clientY-sy));el.style.left=node.x+'px';el.style.top=node.y+'px';drawLinks()};
    const up=()=>{el.removeEventListener('pointermove',move);el.removeEventListener('pointerup',up)};el.addEventListener('pointermove',move);el.addEventListener('pointerup',up);
  });
}
function selectNode(id){selectedId=id;render()}
function updateInspector(){
  const node=topology.nodes.find(n=>n.id===selectedId),card=$('#ntsInspectorCard');card.hidden=!node;if(!node)return;
  $('#ntsNodeName').value=node.name;$('#ntsNodeIp').value=node.ip||'';$('#ntsNodeVendor').value=node.vendor||'Generic';
}
function updateSummary(){const values=$$('#ntsSummary strong');values[0].textContent=topology.nodes.length;values[1].textContent=topology.links.length;values[2].textContent=topology.vlans.length}
function audit(){
  const findings=[],clouds=topology.nodes.filter(n=>n.type==='cloud'),cores=topology.nodes.filter(n=>n.name.toLowerCase().includes('core'));
  if(clouds.length>1)findings.push(['ok','bi-check-circle','Dual upstream paths detected.']);else findings.push(['warning','bi-exclamation-triangle','Single ISP creates an upstream failure risk.']);
  if(cores.length>1)findings.push(['ok','bi-check-circle','Redundant core layer detected.']);else findings.push(['warning','bi-exclamation-triangle','Core layer is a single point of failure.']);
  const linked=new Set(topology.links.flatMap(l=>[l.from,l.to]));const orphan=topology.nodes.filter(n=>!linked.has(n.id));if(orphan.length)findings.push(['error','bi-x-circle',orphan.length+' disconnected device(s) found.']);
  const ips=topology.nodes.map(n=>n.ip).filter(Boolean),duplicates=ips.filter((ip,i)=>ips.indexOf(ip)!==i);if(duplicates.length)findings.push(['error','bi-x-circle','Duplicate management IP detected: '+duplicates[0]]);else findings.push(['ok','bi-check-circle','No duplicate management IP detected.']);
  if(topology.vlans.length)findings.push(['ok','bi-check-circle','VLAN plan detected: '+topology.vlans.join(', ')+'.']);else findings.push(['warning','bi-exclamation-triangle','No VLAN plan was found in the prompt.']);
  const score=Math.max(0,100-findings.filter(f=>f[0]==='warning').length*12-findings.filter(f=>f[0]==='error').length*25);$('#ntsScore').textContent='Score '+score;
  $('#ntsAudit').innerHTML=findings.map(f=>'<div class="nts-audit-item '+(f[0]==='ok'?'':f[0])+'"><i class="bi '+f[1]+'"></i><span>'+escapeHtml(f[2])+'</span></div>').join('');
  log('Design audit completed with a score of '+score+'.','AUDIT');return score;
}
function simulate(kind){
  failure=kind==='reset'?null:kind;topology.nodes.forEach(n=>n.failed=false);topology.links.forEach(l=>l.status='healthy');
  if(!failure){log('All simulated failures cleared. Network restored.','RECOVERY');render();return}
  if(kind==='primary'){
    const isp=topology.nodes.filter(n=>n.type==='cloud')[0];if(isp)isp.failed=true;
    topology.links.filter(l=>l.from===isp?.id).forEach(l=>l.status='failed');const backup=topology.nodes.filter(n=>n.type==='cloud')[1];if(backup)topology.links.filter(l=>l.from===backup.id).forEach(l=>l.status='active');
    log(backup?'Primary ISP failed. Traffic moved to the backup WAN.':'Primary ISP failed. No backup upstream is available.',backup?'FAILOVER':'OUTAGE');
  }else if(kind==='core'){
    const cores=topology.nodes.filter(n=>n.name.toLowerCase().includes('core')),target=cores[0];if(target)target.failed=true;topology.links.filter(l=>l.from===target?.id||l.to===target?.id).forEach(l=>l.status='failed');if(cores[1])topology.links.filter(l=>l.from===cores[1].id||l.to===cores[1].id).forEach(l=>{if(l.status!=='failed')l.status='active'});log(cores[1]?'Core failure isolated. Secondary core is carrying reachable paths.':'Core failed. The design has a single point of failure.',cores[1]?'REROUTE':'OUTAGE');
  }else{
    const target=topology.links.find(l=>/trunk|uplink/i.test(l.label));if(target)target.status='failed';log('Access uplink failure injected. Check the highlighted path and affected branch.','ALARM');
  }
  render();
}
function addDevice(type){
  const node=makeNode(type,labels[type],3,0,1);node.x=Math.max(20,canvas.clientWidth/2-63);node.y=Math.max(20,canvas.clientHeight/2-36);topology.nodes.push(node);selectedId=node.id;render();audit();log(labels[type]+' added to the canvas.','DESIGN');
}
function download(name,type,data){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}
function exportSvg(){
  const w=Math.max(canvas.clientWidth,800),h=Math.max(canvas.clientHeight,560);let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><rect width="100%" height="100%" fill="#081421"/>`;
  topology.links.forEach(l=>{const a=topology.nodes.find(n=>n.id===l.from),b=topology.nodes.find(n=>n.id===l.to);if(a&&b)svg+=`<line x1="${a.x+63}" y1="${a.y+36}" x2="${b.x+63}" y2="${b.y+36}" stroke="${l.status==='failed'?'#fb7185':'#22d3ee'}" stroke-width="2"/><text x="${(a.x+b.x)/2+63}" y="${(a.y+b.y)/2+30}" fill="#8ca2b7" text-anchor="middle" font-family="sans-serif" font-size="10">${escapeHtml(l.label)}</text>`});
  topology.nodes.forEach(n=>{svg+=`<g transform="translate(${n.x} ${n.y})"><rect width="126" height="72" rx="12" fill="#112338" stroke="${n.failed?'#fb7185':'#34d399'}"/><text x="63" y="32" fill="#e9f2fb" text-anchor="middle" font-family="sans-serif" font-weight="700" font-size="11">${escapeHtml(n.name)}</text><text x="63" y="49" fill="#8ca2b7" text-anchor="middle" font-family="sans-serif" font-size="8">${escapeHtml(n.vendor)} · ${escapeHtml(labels[n.type])}</text></g>`});
  svg+='</svg>';download('noc-twin-topology.svg','image/svg+xml',svg);log('Topology exported as SVG.','EXPORT');
}

$('#ntsGenerate').addEventListener('click',()=>{if(!prompt.value.trim())return;topology=parsePrompt(prompt.value);selectedId=null;failure=null;autoLayout(false);audit();log('Digital twin generated from the network requirement.','GENERATED')});
$$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{prompt.value=b.dataset.prompt;prompt.focus()}));
$$('#ntsDevicePalette [data-type]').forEach(b=>b.addEventListener('click',()=>addDevice(b.dataset.type)));
$$('#ntsFailureList [data-failure]').forEach(b=>b.addEventListener('click',()=>{$$('#ntsFailureList button').forEach(x=>x.classList.toggle('active',x===b&&b.dataset.failure!=='reset'));simulate(b.dataset.failure)}));
$$('.nts-mode-tabs button').forEach(b=>b.addEventListener('click',()=>{$$('.nts-mode-tabs button').forEach(x=>x.classList.toggle('active',x===b));if(b.dataset.mode==='validate')audit();if(b.dataset.mode==='simulate')log('Failure Lab armed. Choose a failure scenario.','SIMULATION')}));
$('#ntsAutoLayout').addEventListener('click',autoLayout);$('#ntsExportJson').addEventListener('click',()=>{download('noc-twin-topology.json','application/json',JSON.stringify(topology,null,2));log('Topology exported as structured JSON.','EXPORT')});$('#ntsExportSvg').addEventListener('click',exportSvg);
$('#ntsReset').addEventListener('click',()=>{topology={nodes:[],links:[],vlans:[]};selectedId=null;failure=null;render();$('#ntsAudit').innerHTML='<div class="nts-audit-empty"><i class="bi bi-clipboard-data"></i><span>Generate a design to run the network audit.</span></div>';$('#ntsScore').textContent='Score —';log('Canvas reset.','RESET')});
$('#ntsDeleteNode').addEventListener('click',()=>{if(!selectedId)return;topology.nodes=topology.nodes.filter(n=>n.id!==selectedId);topology.links=topology.links.filter(l=>l.from!==selectedId&&l.to!==selectedId);selectedId=null;render();audit()});
['ntsNodeName','ntsNodeIp','ntsNodeVendor'].forEach(id=>$('#'+id).addEventListener('input',()=>{const n=topology.nodes.find(x=>x.id===selectedId);if(!n)return;n.name=$('#ntsNodeName').value||labels[n.type];n.ip=$('#ntsNodeIp').value;n.vendor=$('#ntsNodeVendor').value;render()}));
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(topology.nodes.length)autoLayout(false);else drawLinks()},120)});render();
})();

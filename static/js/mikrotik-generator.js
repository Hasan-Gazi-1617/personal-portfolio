(function(){
'use strict';
const $=id=>document.getElementById(id);
const panels=[...document.querySelectorAll('.mtg-panel')];
const stepButtons=[...document.querySelectorAll('.mtg-steps button')];
let current=0;
const ip=/^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)$/;
const cidr=/^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\/(?:[0-9]|[12]\d|3[0-2])$/;
function clean(v){return String(v||'').replace(/[\r\n"]/g,'').trim()}
function q(v){return '"'+clean(v)+'"'}
function wanType(){return document.querySelector('input[name="wanType"]:checked').value}
function selectedPorts(){return [...document.querySelectorAll('#lanPorts input:checked')].map(x=>x.value)}
function setVisible(id,on){$(id).hidden=!on}
function syncConditional(){
 const w=wanType();setVisible('staticFields',w==='static');setVisible('pppoeFields',w==='pppoe');
 setVisible('dhcpFields',$('enableDhcp').checked);setVisible('vlanFields',$('enableVlan').checked);setVisible('queueFields',$('enableQueue').checked);
 setVisible('pppoeServerFields',$('enablePppoeServer').checked);setVisible('hotspotFields',$('enableHotspot').checked);setVisible('failoverFields',$('enableFailover').checked);setVisible('remoteFields',$('enableRemote').checked);
}
function validate(panelIndex=current){
 const errors=[];document.querySelectorAll('.invalid').forEach(x=>x.classList.remove('invalid'));
 const add=(id,msg)=>{errors.push(msg);$(id)?.classList.add('invalid')};
 const name=clean($('identity').value);if(!name||!/^[A-Za-z0-9_. -]+$/.test(name))add('identity','Enter a valid router identity.');
 if(panelIndex>=1||panelIndex===7){
  if(wanType()==='static'){if(!cidr.test(clean($('wanIp').value)))add('wanIp','Enter WAN IP in CIDR format.');if(!ip.test(clean($('gateway').value)))add('gateway','Enter a valid WAN gateway.')}
  if(wanType()==='pppoe'){if(!clean($('pppoeUser').value))add('pppoeUser','PPPoE username is required.');if(!clean($('pppoePass').value))add('pppoePass','PPPoE password is required.')}
 }
 if(panelIndex>=2||panelIndex===7){if(!clean($('bridgeName').value))add('bridgeName','Bridge name is required.');if(!cidr.test(clean($('lanIp').value)))add('lanIp','Enter the LAN gateway in CIDR format.');if(!selectedPorts().length)errors.push('Select at least one LAN bridge port.');if(selectedPorts().includes($('wanInterface').value))errors.push('WAN interface cannot also be a LAN bridge port.')}
 if((panelIndex>=3||panelIndex===7)&&$('enableDhcp').checked){['poolStart','poolEnd'].forEach(id=>{if(!ip.test(clean($(id).value)))add(id,'Enter valid DHCP pool addresses.')});if(!cidr.test(clean($('dhcpNetwork').value)))add('dhcpNetwork','Enter DHCP network in CIDR format.')}
 if(panelIndex>=3||panelIndex===7){if(!ip.test(clean($('dns1').value)))add('dns1','Primary DNS is invalid.');if(clean($('dns2').value)&&!ip.test(clean($('dns2').value)))add('dns2','Secondary DNS is invalid.')}
 if((panelIndex>=4||panelIndex===7)&&$('enableVlan').checked){const id=+$('vlanId').value;if(id<1||id>4094)add('vlanId','VLAN ID must be 1–4094.');if(!cidr.test(clean($('vlanIp').value)))add('vlanIp','Enter VLAN gateway in CIDR format.')}
 if((panelIndex>=6||panelIndex===7)&&$('enableQueue').checked&&!cidr.test(clean($('queueTarget').value)))add('queueTarget','Queue target must use CIDR format.');
 if(panelIndex>=6||panelIndex===7){
  if($('enablePppoeServer').checked){if(!ip.test(clean($('pppoeLocal').value)))add('pppoeLocal','Enter a valid PPPoE local address.');if(!poolRangeValid($('pppoePool').value))add('pppoePool','PPPoE pool must be startIP-endIP.');if(!clean($('pppoeSecretUser').value))add('pppoeSecretUser','PPPoE test username is required.');if(!clean($('pppoeSecretPass').value))add('pppoeSecretPass','PPPoE test password is required.')}
  if($('enableHotspot').checked){if(!cidr.test(clean($('hotspotGateway').value)))add('hotspotGateway','Hotspot gateway must use CIDR format.');if(!poolRangeValid($('hotspotPool').value))add('hotspotPool','Hotspot pool must be startIP-endIP.');if(!clean($('hotspotDnsName').value))add('hotspotDnsName','Hotspot DNS name is required.');if(!clean($('hotspotUser').value))add('hotspotUser','Hotspot admin username is required.');if(!clean($('hotspotPass').value))add('hotspotPass','Hotspot admin password is required.')}
  if($('enableFailover').checked){if(!ip.test(clean($('backupGateway').value)))add('backupGateway','Enter a valid backup gateway.');const pd=+$('primaryDistance').value,bd=+$('backupDistance').value;if(pd<1||pd>250)add('primaryDistance','Primary distance must be 1–250.');if(bd<2||bd>250||bd<=pd)add('backupDistance','Backup distance must be greater than primary distance.');if($('backupWan').value===$('wanInterface').value)add('backupWan','Backup WAN must differ from primary WAN.');}
  if($('enableRemote').checked){if(!cidr.test(clean($('remoteSource').value)))add('remoteSource','Management source must use CIDR format.');const wp=+$('winboxPort').value;if(wp<1||wp>65535)add('winboxPort','Winbox port must be 1–65535.');}
 }
 const box=$('validationSummary');box.hidden=!errors.length;box.innerHTML=errors.length?'<i class="bi bi-exclamation-triangle"></i><div><strong>Please fix:</strong><ul><li>'+errors.join('</li><li>')+'</li></ul></div>':'';
 return !errors.length;
}
function networkFromCidr(v){return clean(v).split('/')[0]}
function poolRangeValid(v){const p=clean(v).split('-');return p.length===2&&ip.test(p[0])&&ip.test(p[1])}
function gatewayAddress(v){return networkFromCidr(v)}
function buildScript(){
 const lines=[];const wan=$('wanInterface').value;const bridge=clean($('bridgeName').value);const w=wanType();
 lines.push('# MikroTik RouterOS v'+$('routerOsVersion').value+' configuration');
 lines.push('# '+clean($('configLabel').value));
 lines.push('# Review before import. Existing configuration is not removed.');
 lines.push('');
 lines.push('# ---------- SYSTEM ----------');
 lines.push('/system identity set name='+q($('identity').value));
 lines.push('/system clock set time-zone-name='+q($('timezone').value));
 lines.push('/interface ethernet set [find default-name='+wan+'] comment='+q($('wanComment').value));
 lines.push('');
 lines.push('# ---------- WAN ----------');
 if(w==='dhcp')lines.push('/ip dhcp-client add interface='+wan+' add-default-route=yes use-peer-dns=no disabled=no comment="ISP DHCP"');
 if(w==='static'){lines.push('/ip address add address='+clean($('wanIp').value)+' interface='+wan+' comment="ISP STATIC"');const routeOptions=$('enableFailover').checked?' distance='+$('primaryDistance').value+' check-gateway=ping':'';lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('gateway').value)+routeOptions+' comment="DEFAULT ROUTE"');}
 if(w==='pppoe'){const mtu=$('pppoeMru').checked?' max-mtu=1480 max-mru=1480':'';lines.push('/interface pppoe-client add name=pppoe-out1 interface='+wan+' user='+q($('pppoeUser').value)+' password='+q($('pppoePass').value)+' add-default-route=yes use-peer-dns=no disabled=no'+mtu+' comment="ISP PPPOE"');}
 lines.push('');
 lines.push('# ---------- BRIDGE & LAN ----------');
 lines.push('/interface bridge add name='+bridge+' protocol-mode=rstp comment="LAN BRIDGE"');
 selectedPorts().forEach(p=>lines.push('/interface bridge port add bridge='+bridge+' interface='+p+' comment="LAN PORT"'));
 lines.push('/ip address add address='+clean($('lanIp').value)+' interface='+bridge+' comment="LAN GATEWAY"');
 lines.push('');
 lines.push('# ---------- DNS ----------');
 const dns=[clean($('dns1').value),clean($('dns2').value)].filter(Boolean).join(',');
 lines.push('/ip dns set servers='+dns+' allow-remote-requests=yes');
 if($('enableDhcp').checked){
  lines.push('');
  lines.push('# ---------- DHCP SERVER ----------');
  lines.push('/ip pool add name=pool-LAN ranges='+clean($('poolStart').value)+'-'+clean($('poolEnd').value));
  lines.push('/ip dhcp-server add name=dhcp-LAN interface='+bridge+' address-pool=pool-LAN lease-time='+$('leaseTime').value+' disabled=no');
  lines.push('/ip dhcp-server network add address='+clean($('dhcpNetwork').value)+' gateway='+networkFromCidr($('lanIp').value)+' dns-server='+dns);
 }
 if($('enableVlan').checked){
  lines.push('');lines.push('# ---------- VLAN ----------');
  const vn=clean($('vlanName').value);lines.push('/interface vlan add name='+vn+' vlan-id='+$('vlanId').value+' interface='+clean($('vlanParent').value)+' comment="TAGGED VLAN"');
  lines.push('/ip address add address='+clean($('vlanIp').value)+' interface='+vn+' comment="VLAN GATEWAY"');
 }
 if($('enableNat').checked){
  lines.push('');lines.push('# ---------- NAT ----------');
  const out=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall nat add chain=srcnat out-interface='+out+' action=masquerade comment="LAN TO INTERNET"');
 }
 if($('enableFirewall').checked){
  lines.push('');lines.push('# ---------- BASELINE FIREWALL ----------');
  lines.push('/ip firewall filter add chain=input action=accept connection-state=established,related,untracked comment="ACCEPT ESTABLISHED"');
  lines.push('/ip firewall filter add chain=input action=drop connection-state=invalid comment="DROP INVALID"');
  lines.push('/ip firewall filter add chain=input action=accept protocol=icmp comment="ALLOW ICMP"');
  lines.push('/ip firewall filter add chain=input action=accept in-interface='+bridge+' comment="ALLOW LAN MANAGEMENT"');
  if($('enableRemote').checked)lines.push('/ip firewall filter add chain=input action=accept protocol=tcp src-address='+clean($('remoteSource').value)+' dst-port=22,'+$('winboxPort').value+' comment="ALLOW RESTRICTED REMOTE MANAGEMENT"');
  const inIf=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall filter add chain=input action=drop in-interface='+inIf+' comment="DROP UNSOLICITED WAN INPUT"');
 }
 if($('disableServices').checked){
  lines.push('');lines.push('# ---------- MANAGEMENT SERVICES ----------');
  ['telnet','ftp','api','api-ssl'].forEach(service=>lines.push('/ip service set [find name='+service+'] disabled=yes'));
  const managementSource=$('enableRemote').checked?clean($('remoteSource').value):clean($('dhcpNetwork').value);
  lines.push('/ip service set [find name=ssh] disabled=no address='+managementSource);
  lines.push('/ip service set [find name=winbox] disabled=no address='+managementSource+($('enableRemote').checked?' port='+$('winboxPort').value:''));
 }
 if($('enableQueue').checked){
  lines.push('');lines.push('# ---------- SIMPLE QUEUE ----------');
  lines.push('/queue simple add name='+q($('queueName').value)+' target='+clean($('queueTarget').value)+' max-limit='+$('uploadLimit').value+'/'+$('downloadLimit').value+' comment="GENERATED BANDWIDTH LIMIT"');
 }
 if($('enablePppoeServer').checked){
  lines.push('');lines.push('# ---------- PPPOE SERVER ----------');
  lines.push('/ip pool add name=pool-PPPOE ranges='+clean($('pppoePool').value));
  lines.push('/ppp profile add name=profile-PPPOE local-address='+clean($('pppoeLocal').value)+' remote-address=pool-PPPOE dns-server='+dns+' only-one=yes');
  lines.push('/interface pppoe-server server add interface='+clean($('pppoeServerInterface').value)+' service-name='+q($('pppoeServiceName').value)+' default-profile=profile-PPPOE one-session-per-host=yes disabled=no');
  lines.push('/ppp secret add name='+q($('pppoeSecretUser').value)+' password='+q($('pppoeSecretPass').value)+' service=pppoe profile=profile-PPPOE');
 }
 if($('enableHotspot').checked){
  lines.push('');lines.push('# ---------- HOTSPOT ----------');
  const hsIf=clean($('hotspotInterface').value),hsGateway=clean($('hotspotGateway').value);
  lines.push('/ip pool add name=pool-HOTSPOT ranges='+clean($('hotspotPool').value));
  lines.push('/ip address add address='+hsGateway+' interface='+hsIf+' comment="HOTSPOT GATEWAY"');
  lines.push('/ip hotspot profile add name=hsprof-GENERATED hotspot-address='+gatewayAddress(hsGateway)+' dns-name='+q($('hotspotDnsName').value)+' html-directory=hotspot');
  lines.push('/ip hotspot add name=hotspot-GENERATED interface='+hsIf+' address-pool=pool-HOTSPOT profile=hsprof-GENERATED disabled=no');
  lines.push('/ip hotspot user add name='+q($('hotspotUser').value)+' password='+q($('hotspotPass').value)+' profile=default');
 }
 if($('enableFailover').checked){
  lines.push('');lines.push('# ---------- MULTI-WAN FAILOVER ----------');
  lines.push('/interface ethernet set [find default-name='+$('backupWan').value+'] comment="BACKUP WAN"');
  lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('backupGateway').value)+' distance='+$('backupDistance').value+' check-gateway=ping comment="BACKUP DEFAULT ROUTE"');
 }
 if($('enableRemote').checked&&!$('disableServices').checked){
  lines.push('');lines.push('# ---------- SECURE REMOTE ACCESS ----------');
  lines.push('/ip service set [find name=ssh] disabled=no address='+clean($('remoteSource').value));
  lines.push('/ip service set [find name=winbox] disabled=no address='+clean($('remoteSource').value)+' port='+$('winboxPort').value);
 }
 lines.push('');lines.push('# ---------- END ----------');lines.push(':log info "Hasan MikroTik generated configuration applied"');
 return lines.join('\n');
}
function renderReview(){
 if(!validate(7))return false;
 const script=buildScript();$('scriptOutput').textContent=script;$('lineCount').textContent=script.split('\n').filter(x=>x&& !x.startsWith('#')).length+' commands';renderCommandRows(script);
 $('topologyRouter').textContent=clean($('identity').value)||'Router';
 const values=[['RouterOS','v'+$('routerOsVersion').value],['WAN',wanType().toUpperCase()],['Uplink',$('wanInterface').value],['LAN',clean($('lanIp').value)],['Bridge ports',selectedPorts().join(', ')],['DHCP',$('enableDhcp').checked?'Enabled':'Disabled'],['VLAN',$('enableVlan').checked?'VLAN '+$('vlanId').value:'Disabled'],['Firewall',$('enableFirewall').checked?'Baseline':'Disabled'],['Queue',$('enableQueue').checked?clean($('queueTarget').value):'Disabled'],['PPPoE Server',$('enablePppoeServer').checked?'Enabled':'Disabled'],['Hotspot',$('enableHotspot').checked?'Enabled':'Disabled'],['Failover',$('enableFailover').checked?'Enabled':'Disabled'],['Remote',$('enableRemote').checked?clean($('remoteSource').value):'Disabled']];
 $('configSummary').innerHTML=values.map(v=>'<div><small>'+v[0]+'</small><b>'+v[1]+'</b></div>').join('');
 return true;
}
function show(index){
 if(index<0||index>=panels.length)return;
 current=index;panels.forEach((p,i)=>p.classList.toggle('active',i===index));stepButtons.forEach((b,i)=>b.classList.toggle('active',i===index));
 $('progressText').textContent=(index+1)+' / '+panels.length;$('progressBar').style.width=((index+1)/panels.length*100)+'%';
 $('prevStep').disabled=index===0;$('nextStep').innerHTML=index===panels.length-1?'Regenerate <i class="bi bi-arrow-clockwise"></i>':'Next step <i class="bi bi-arrow-right"></i>';
 if(index===panels.length-1)renderReview();window.scrollTo({top:document.querySelector('.mtg-workspace').offsetTop-90,behavior:'smooth'});
}
stepButtons.forEach((b,i)=>b.addEventListener('click',()=>{if(i>current&&!validate(current))return;show(i)}));
document.querySelectorAll('[data-jump]').forEach(button=>button.addEventListener('click',()=>{
 const index=panels.findIndex(panel=>panel.dataset.panel===button.dataset.jump);
 if(index<0)return;
 if(index>current&&!validate(current))return;
 show(index);
}));
$('routerOsVersion').addEventListener('change',()=>{
 const badge=$('targetVersionBadge');if(badge)badge.textContent='RouterOS v'+$('routerOsVersion').value;
});
$('nextStep').addEventListener('click',()=>{if(current===panels.length-1){renderReview();return}if(validate(current))show(current+1)});
$('prevStep').addEventListener('click',()=>show(current-1));
document.querySelectorAll('input[name="wanType"],#enableDhcp,#enableVlan,#enableQueue,#enablePppoeServer,#enableHotspot,#enableFailover,#enableRemote').forEach(x=>x.addEventListener('change',syncConditional));
$('bridgeName').addEventListener('input',()=>{if($('vlanParent').options[0]){$('vlanParent').options[0].value=clean($('bridgeName').value);$('vlanParent').options[0].textContent=clean($('bridgeName').value)||'Bridge'}});
$('copyScript').addEventListener('click',async function(){if(!renderReview())return;try{await navigator.clipboard.writeText($('scriptOutput').textContent);const old=this.innerHTML;this.innerHTML='<i class="bi bi-check2"></i> Copied';this.classList.add('is-success');setTimeout(()=>{this.innerHTML=old;this.classList.remove('is-success')},1600)}catch(e){alert('Copy failed. Select the script manually.')}});
$('downloadScript').addEventListener('click',()=>{if(!renderReview())return;const blob=new Blob([$('scriptOutput').textContent],{type:'text/plain;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(clean($('identity').value)||'mikrotik-router').replace(/\s+/g,'-').toLowerCase()+'.rsc';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});

function executableCommands(script){
 return script.split('\n').map(x=>x.trim()).filter(x=>x&&!x.startsWith('#')&&!x.startsWith(':log'));
}
function renderCommandRows(script,results){
 const commands=executableCommands(script);const box=$('commandResults');if(!box)return;
 box.innerHTML=commands.map((cmd,i)=>{
  const r=results&&results[i];const state=r?(r.success?'success':'failed'):'ready';
  const label=r?(r.success?'Success':'Failed'):'Ready';
  const detail=r&&r.output?'<small class="mtg-result-detail">'+escapeHtml(r.output)+'</small>':'';
  return '<div class="mtg-result-row"><span class="mtg-result-index">'+String(i+1).padStart(2,'0')+'</span><code class="mtg-result-command">'+escapeHtml(cmd)+detail+'</code><span class="mtg-result-status '+state+'">'+label+'</span></div>';
 }).join('')||'<div class="mtg-result-empty">No executable commands generated.</div>';
}
function escapeHtml(value){const e=document.createElement('div');e.textContent=String(value||'');return e.innerHTML}
function agentBase(){return clean($('agentUrl').value).replace(/\/$/,'')}
function agentHeaders(){return {'Content-Type':'application/json','X-MTG-Token':$('agentToken').value}}
function setAgentState(text,state){const el=$('agentState');el.textContent=text;el.className='mtg-agent-state '+(state||'')}
async function testAgent(){
 setAgentState('Connecting…','');
 try{
  const res=await fetch(agentBase()+'/health',{headers:agentHeaders()});const data=await res.json();
  if(!res.ok)throw new Error(data.error||'Agent rejected connection');
  setAgentState('Connected · '+data.platform,'connected');
 }catch(e){setAgentState('Connection failed','failed');throw e}
}
$('testAgent')?.addEventListener('click',async function(){
 try{await testAgent()}catch(e){alert('Local agent connection failed: '+e.message)}
});
$('runLive')?.addEventListener('click',async function(){
 if(!renderReview())return;
 const commands=executableCommands($('scriptOutput').textContent);
 if(!clean($('routerHost').value)||!clean($('routerUser').value)||!$('routerPassword').value){alert('Enter router host, username and password.');return}
 if(!confirm('A timestamped backup will be requested first. Execute '+commands.length+' commands on '+clean($('routerHost').value)+'?'))return;
 this.disabled=true;this.innerHTML='<i class="bi bi-hourglass-split"></i> Running…';
 try{
  await testAgent();
  $('commandResults').querySelectorAll('.mtg-result-status').forEach(x=>{x.className='mtg-result-status queued';x.textContent='Queued'});
  const res=await fetch(agentBase()+'/execute',{method:'POST',headers:agentHeaders(),body:JSON.stringify({
   router:{host:clean($('routerHost').value),port:Number($('routerPort').value),username:clean($('routerUser').value),password:$('routerPassword').value},
   routeros_version:$('routerOsVersion').value,commands:commands,stop_on_error:$('stopOnError').checked,create_backup:true
  })});
  const data=await res.json();if(!res.ok)throw new Error(data.error||'Execution failed');
  renderCommandRows($('scriptOutput').textContent,data.results||[]);
  const failed=(data.results||[]).filter(x=>!x.success).length;
  setAgentState(failed?failed+' command failed':'All commands successful',failed?'failed':'connected');
 }catch(e){setAgentState('Execution failed','failed');alert('Execution stopped: '+e.message)}
 finally{this.disabled=false;this.innerHTML='<i class="bi bi-play-fill"></i> Backup & Execute'}
});

syncConditional();show(0);
})();
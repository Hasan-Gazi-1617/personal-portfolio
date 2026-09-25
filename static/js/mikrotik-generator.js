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
 const box=$('validationSummary');box.hidden=!errors.length;box.innerHTML=errors.length?'<i class="bi bi-exclamation-triangle"></i><div><strong>Please fix:</strong><ul><li>'+errors.join('</li><li>')+'</li></ul></div>':'';
 return !errors.length;
}
function networkFromCidr(v){return clean(v).split('/')[0]}
function buildScript(){
 const lines=[];const wan=$('wanInterface').value;const bridge=clean($('bridgeName').value);const w=wanType();
 lines.push('# MikroTik RouterOS v7 configuration');
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
 if(w==='static'){lines.push('/ip address add address='+clean($('wanIp').value)+' interface='+wan+' comment="ISP STATIC"');lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('gateway').value)+' comment="DEFAULT ROUTE"');}
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
  const inIf=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall filter add chain=input action=drop in-interface='+inIf+' comment="DROP UNSOLICITED WAN INPUT"');
 }
 if($('disableServices').checked){
  lines.push('');lines.push('# ---------- MANAGEMENT SERVICES ----------');
  lines.push('/ip service disable telnet,ftp,api,api-ssl');
  lines.push('/ip service set ssh address='+clean($('dhcpNetwork').value));
  lines.push('/ip service set winbox address='+clean($('dhcpNetwork').value));
 }
 if($('enableQueue').checked){
  lines.push('');lines.push('# ---------- SIMPLE QUEUE ----------');
  lines.push('/queue simple add name='+q($('queueName').value)+' target='+clean($('queueTarget').value)+' max-limit='+$('uploadLimit').value+'/'+$('downloadLimit').value+' comment="GENERATED BANDWIDTH LIMIT"');
 }
 lines.push('');lines.push('# ---------- END ----------');lines.push(':log info "Hasan MikroTik generated configuration applied"');
 return lines.join('\n');
}
function renderReview(){
 if(!validate(7))return false;
 const script=buildScript();$('scriptOutput').textContent=script;$('lineCount').textContent=script.split('\n').filter(x=>x&& !x.startsWith('#')).length+' commands';
 $('topologyRouter').textContent=clean($('identity').value)||'Router';
 const values=[['WAN',wanType().toUpperCase()],['Uplink',$('wanInterface').value],['LAN',clean($('lanIp').value)],['Bridge ports',selectedPorts().join(', ')],['DHCP',$('enableDhcp').checked?'Enabled':'Disabled'],['VLAN',$('enableVlan').checked?'VLAN '+$('vlanId').value:'Disabled'],['Firewall',$('enableFirewall').checked?'Baseline':'Disabled'],['Queue',$('enableQueue').checked?clean($('queueTarget').value):'Disabled']];
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
$('nextStep').addEventListener('click',()=>{if(current===panels.length-1){renderReview();return}if(validate(current))show(current+1)});
$('prevStep').addEventListener('click',()=>show(current-1));
document.querySelectorAll('input[name="wanType"],#enableDhcp,#enableVlan,#enableQueue').forEach(x=>x.addEventListener('change',syncConditional));
$('bridgeName').addEventListener('input',()=>{if($('vlanParent').options[0]){$('vlanParent').options[0].value=clean($('bridgeName').value);$('vlanParent').options[0].textContent=clean($('bridgeName').value)||'Bridge'}});
$('copyScript').addEventListener('click',async function(){if(!renderReview())return;try{await navigator.clipboard.writeText($('scriptOutput').textContent);const old=this.innerHTML;this.innerHTML='<i class="bi bi-check2"></i> Copied';this.classList.add('is-success');setTimeout(()=>{this.innerHTML=old;this.classList.remove('is-success')},1600)}catch(e){alert('Copy failed. Select the script manually.')}});
$('downloadScript').addEventListener('click',()=>{if(!renderReview())return;const blob=new Blob([$('scriptOutput').textContent],{type:'text/plain;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(clean($('identity').value)||'mikrotik-router').replace(/\s+/g,'-').toLowerCase()+'.rsc';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});
syncConditional();show(0);
})();
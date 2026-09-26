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
 setVisible('burstFields',$('enableQueue').checked&&$('enableBurst').checked);setVisible('wifiFields',$('enableWifi').checked);
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
 if((panelIndex>=4||panelIndex===7)&&$('enableVlan').checked){const id=+$('vlanId').value;if(id<1||id>4094)add('vlanId','VLAN ID must be 1–4094.');if(!cidr.test(clean($('vlanIp').value)))add('vlanIp','Enter VLAN gateway in CIDR format.');if($('enableVlanFiltering').checked&&!clean($('vlanTaggedPorts').value))add('vlanTaggedPorts','Enter at least one tagged trunk port.')}
 if((panelIndex>=6||panelIndex===7)&&$('enableQueue').checked){
  if(!cidr.test(clean($('queueTarget').value)))add('queueTarget','Queue target must use CIDR format.');
  if($('enableBurst').checked&&(!clean($('burstLimit').value)||!clean($('burstThreshold').value)||!clean($('burstTime').value)))errors.push('Complete all burst settings.');
 }
 if((panelIndex>=6||panelIndex===7)&&$('enableWifi').checked){if(!clean($('wifiSsid').value))add('wifiSsid','Wi-Fi SSID is required.');if(clean($('wifiPassword').value).length<8)add('wifiPassword','Wi-Fi password must be at least 8 characters.');}
 if((panelIndex>=6||panelIndex===7)&&$('enableFailover').checked&&$('enableNetwatch').checked&&!ip.test(clean($('netwatchHost').value)))add('netwatchHost','Enter a valid Netwatch host IP.');
 if(panelIndex>=6||panelIndex===7){
  if($('enablePppoeServer').checked){if(!ip.test(clean($('pppoeLocal').value)))add('pppoeLocal','Enter a valid PPPoE local address.');if(!poolRangeValid($('pppoePool').value))add('pppoePool','PPPoE pool must be startIP-endIP.');if(!clean($('pppoeSecretUser').value))add('pppoeSecretUser','PPPoE test username is required.');if(!clean($('pppoeSecretPass').value))add('pppoeSecretPass','PPPoE test password is required.')}
  if($('enableHotspot').checked){if(!cidr.test(clean($('hotspotGateway').value)))add('hotspotGateway','Hotspot gateway must use CIDR format.');if(!poolRangeValid($('hotspotPool').value))add('hotspotPool','Hotspot pool must be startIP-endIP.');if(!clean($('hotspotDnsName').value))add('hotspotDnsName','Hotspot DNS name is required.');if(!clean($('hotspotUser').value))add('hotspotUser','Hotspot admin username is required.');if(!clean($('hotspotPass').value))add('hotspotPass','Hotspot admin password is required.')}
  if($('enableFailover').checked){const bt=$('backupWanType').value;if(bt==='static'){if(!cidr.test(clean($('backupIp').value)))add('backupIp','Enter backup IP in CIDR format.');if(!ip.test(clean($('backupGateway').value)))add('backupGateway','Enter a valid backup gateway.');}if(bt==='pppoe'&&(!clean($('backupUser').value)||!clean($('backupPass').value)))errors.push('Backup PPPoE username and password are required.');const pd=+$('primaryDistance').value,bd=+$('backupDistance').value;if(pd<1||pd>250)add('primaryDistance','Primary distance must be 1–250.');if(bd<2||bd>250||bd<=pd)add('backupDistance','Backup distance must be greater than primary distance.');if($('backupWan').value===$('wanInterface').value)add('backupWan','Backup WAN must differ from primary WAN.');}
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
  if($('enableVlanFiltering').checked){const tagged=clean($('vlanTaggedPorts').value),access=$('vlanAccessPort').value,vid=$('vlanId').value;lines.push('/interface bridge port set [find interface='+access+'] pvid='+vid+' comment="VLAN '+vid+' ACCESS"');lines.push('/interface bridge vlan add bridge='+bridge+' vlan-ids='+vid+' tagged='+bridge+','+tagged+' untagged='+access+' comment="PRODUCTION VLAN '+vid+'"');lines.push('/interface bridge set [find name='+bridge+'] vlan-filtering=yes');}
 }
 if($('enableNat').checked){
  lines.push('');lines.push('# ---------- NAT ----------');
  const out=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall nat add chain=srcnat out-interface='+out+' action=masquerade comment="LAN TO INTERNET"');
 }
 if($('enableFirewall').checked){
  lines.push('');lines.push('# ---------- BASELINE FIREWALL ----------');
  lines.push('/ip firewall filter add chain=input action=accept connection-state=established,related,untracked comment="ACCEPT ESTABLISHED"');
  lines.push('/ip firewall filter add chain=input action=drop connection-state=invalid comment="DROP INVALID"');
  if($('enableIcmpProtection').checked){
   lines.push('/ip firewall filter add chain=input protocol=icmp limit=10,20:packet action=accept comment="LIMIT ICMP"');
   lines.push('/ip firewall filter add chain=input protocol=icmp action=drop comment="DROP ICMP FLOOD"');
  }else lines.push('/ip firewall filter add chain=input action=accept protocol=icmp comment="ALLOW ICMP"');
  lines.push('/ip firewall filter add chain=input action=accept in-interface='+bridge+' comment="ALLOW LAN MANAGEMENT"');
  if($('enablePortScanProtection').checked){
   lines.push('/ip firewall filter add chain=input protocol=tcp psd=21,3s,3,1 action=add-src-to-address-list address-list=port-scanners address-list-timeout=1d comment="DETECT PORT SCAN"');
   lines.push('/ip firewall filter add chain=input src-address-list=port-scanners action=drop comment="DROP PORT SCANNERS"');
  }
  if($('enableBogonProtection').checked){['0.0.0.0/8','10.0.0.0/8','100.64.0.0/10','127.0.0.0/8','169.254.0.0/16','172.16.0.0/12','192.0.0.0/24','192.168.0.0/16','224.0.0.0/3'].forEach(net=>lines.push('/ip firewall address-list add list=BOGONS address='+net+' comment="BOGON SOURCE"'));const bogonWan=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall filter add chain=input in-interface='+bogonWan+' src-address-list=BOGONS action=drop comment="DROP BOGON FROM WAN"');}
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
  const queueMode=$('queueMode').value,priority=$('queuePriority').value,target=clean($('queueTarget').value);
  const burst=$('enableBurst').checked?' burst-limit='+clean($('burstLimit').value)+' burst-threshold='+clean($('burstThreshold').value)+' burst-time='+clean($('burstTime').value):'';
  if(queueMode==='tree'){
   lines.push('');lines.push('# ---------- QUEUE TREE & PRIORITY QOS ----------');
   lines.push('/ip firewall mangle add chain=forward src-address='+target+' action=mark-packet new-packet-mark=CLIENT-UP passthrough=no comment="MARK CLIENT UPLOAD"');
   lines.push('/ip firewall mangle add chain=forward dst-address='+target+' action=mark-packet new-packet-mark=CLIENT-DOWN passthrough=no comment="MARK CLIENT DOWNLOAD"');
   const bl=clean($('burstLimit').value).split('/'),bt=clean($('burstThreshold').value).split('/'),btime=clean($('burstTime').value).split('/');
   const upBurst=$('enableBurst').checked?' burst-limit='+(bl[0]||'')+' burst-threshold='+(bt[0]||'')+' burst-time='+(btime[0]||''):'';
   const downBurst=$('enableBurst').checked?' burst-limit='+(bl[1]||bl[0]||'')+' burst-threshold='+(bt[1]||bt[0]||'')+' burst-time='+(btime[1]||btime[0]||''):'';
   lines.push('/queue tree add name='+q($('queueName').value+'-UPLOAD')+' parent=global packet-mark=CLIENT-UP max-limit='+$('uploadLimit').value+' priority='+priority+upBurst+' comment="CLIENT UPLOAD QOS"');
   lines.push('/queue tree add name='+q($('queueName').value+'-DOWNLOAD')+' parent=global packet-mark=CLIENT-DOWN max-limit='+$('downloadLimit').value+' priority='+priority+downBurst+' comment="CLIENT DOWNLOAD QOS"');
  }else{
   lines.push('');lines.push('# ---------- SIMPLE QUEUE ----------');
   lines.push('/queue simple add name='+q($('queueName').value)+' target='+target+' max-limit='+$('uploadLimit').value+'/'+$('downloadLimit').value+' priority='+priority+'/'+priority+burst+' comment="GENERATED BANDWIDTH LIMIT"');
  }
 }
 if($('enablePppoeServer').checked){
  lines.push('');lines.push('# ---------- PPPOE SERVER ----------');
  lines.push('/ip pool add name=pool-PPPOE ranges='+clean($('pppoePool').value));
  const pppRate=clean($('pppoeRateLimit').value);lines.push('/ppp profile add name=profile-PPPOE local-address='+clean($('pppoeLocal').value)+' remote-address=pool-PPPOE dns-server='+dns+' only-one=yes'+(pppRate?' rate-limit='+pppRate:''));
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
  lines.push('/ip hotspot user profile set [find name=default] idle-timeout='+clean($('hotspotIdleTimeout').value)+' keepalive-timeout=2m');
  lines.push('/ip hotspot user add name='+q($('hotspotUser').value)+' password='+q($('hotspotPass').value)+' profile=default comment="HOTSPOT ADMIN"');
  lines.push('/ip hotspot user add name='+q($('hotspotClientUser').value)+' password='+q($('hotspotClientPass').value)+' profile=default comment="HOTSPOT CLIENT"');
 }
 if($('enableFailover').checked){
  lines.push('');lines.push('# ---------- MULTI-WAN FAILOVER ----------');
  const backupIf=$('backupWan').value,backupType=$('backupWanType').value;lines.push('/interface ethernet set [find default-name='+backupIf+'] comment="BACKUP WAN"');
  if(backupType==='dhcp')lines.push('/ip dhcp-client add interface='+backupIf+' add-default-route=yes default-route-distance='+$('backupDistance').value+' use-peer-dns=no comment="BACKUP DHCP WAN" disabled=no');
  if(backupType==='static'){lines.push('/ip address add address='+clean($('backupIp').value)+' interface='+backupIf+' comment="BACKUP STATIC WAN"');lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('backupGateway').value)+' distance='+$('backupDistance').value+' check-gateway=ping comment="BACKUP DEFAULT ROUTE"');}
  if(backupType==='pppoe')lines.push('/interface pppoe-client add name=pppoe-backup interface='+backupIf+' user='+q($('backupUser').value)+' password='+q($('backupPass').value)+' add-default-route=yes default-route-distance='+$('backupDistance').value+' use-peer-dns=no disabled=no comment="BACKUP PPPOE WAN"');
  if($('enableNetwatch').checked)lines.push('/tool netwatch add host='+clean($('netwatchHost').value)+' interval=10s timeout=3s up-script=":log info PRIMARY-WAN-UP" down-script=":log warning PRIMARY-WAN-DOWN" comment="FAILOVER MONITOR"');
 }
 if($('enableWifi').checked){
  lines.push('');lines.push('# ---------- WI-FI ACCESS POINT ----------');
  const wifiIf=clean($('wifiInterface').value),wifiBridge=clean($('wifiBridge').value),ssid=q($('wifiSsid').value),wifiPass=q($('wifiPassword').value);
  if($('routerOsVersion').value==='7'&&wifiIf.indexOf('wifi')===0){
   lines.push('/interface wifi security add name=sec-GENERATED authentication-types=wpa2-psk passphrase='+wifiPass);
   lines.push('/interface wifi configuration add name=cfg-GENERATED ssid='+ssid+' security=sec-GENERATED');
   lines.push('/interface wifi set [find default-name='+wifiIf+'] configuration=cfg-GENERATED disabled=no');
  }else{
   lines.push('/interface wireless security-profiles add name=sec-GENERATED mode=dynamic-keys authentication-types=wpa2-psk wpa2-pre-shared-key='+wifiPass);
   lines.push('/interface wireless set [find default-name='+wifiIf+'] mode=ap-bridge ssid='+ssid+' security-profile=sec-GENERATED disabled=no');
  }
  lines.push('/interface bridge port add bridge='+wifiBridge+' interface='+wifiIf+' comment="WIFI AP"');
 }
 if($('enableRemote').checked&&!$('disableServices').checked){
  lines.push('');lines.push('# ---------- SECURE REMOTE ACCESS ----------');
  lines.push('/ip service set [find name=ssh] disabled=no address='+clean($('remoteSource').value));
  lines.push('/ip service set [find name=winbox] disabled=no address='+clean($('remoteSource').value)+' port='+$('winboxPort').value);
 }
 if($('enableDiagnostics').checked){lines.push('');lines.push('# ---------- VERIFY & TROUBLESHOOT ----------');lines.push('/interface print terse');lines.push('/ip address print');lines.push('/ip route print');lines.push('/ip firewall filter print stats');if($('enablePppoeServer').checked)lines.push('/ppp active print');if($('enableHotspot').checked){lines.push('/ip hotspot active print');lines.push('/ip hotspot host print');}lines.push('/ping 8.8.8.8 count=4');lines.push('/tool traceroute 8.8.8.8');}
 lines.push('');lines.push('# ---------- END ----------');lines.push(':log info "Hasan MikroTik generated configuration applied"');
 return lines.join('\n');
}
function renderReview(){
 if(!validate(7))return false;
 const script=buildScript();$('scriptOutput').textContent=script;$('lineCount').textContent=script.split('\n').filter(x=>x&& !x.startsWith('#')).length+' commands';renderCommandRows(script);
 $('topologyRouter').textContent=clean($('identity').value)||'Router';
 const values=[['RouterOS','v'+$('routerOsVersion').value],['WAN',wanType().toUpperCase()],['Uplink',$('wanInterface').value],['LAN',clean($('lanIp').value)],['Bridge ports',selectedPorts().join(', ')],['DHCP',$('enableDhcp').checked?'Enabled':'Disabled'],['VLAN',$('enableVlan').checked?'VLAN '+$('vlanId').value+($('enableVlanFiltering').checked?' / Production':' / Interface'):'Disabled'],['Firewall',$('enableFirewall').checked?'Baseline'+($('enableBogonProtection').checked?' + Bogon':''):'Disabled'],['Queue',$('enableQueue').checked?$('queueMode').value+' / '+clean($('queueTarget').value):'Disabled'],['Wi-Fi',$('enableWifi').checked?clean($('wifiSsid').value):'Disabled'],['PPPoE Server',$('enablePppoeServer').checked?'Enabled':'Disabled'],['Hotspot',$('enableHotspot').checked?'Enabled':'Disabled'],['Failover',$('enableFailover').checked?$('backupWanType').value.toUpperCase()+' backup':'Disabled'],['Remote',$('enableRemote').checked?$('remoteMode').value+' / '+clean($('remoteSource').value):'Disabled'],['Diagnostics',$('enableDiagnostics').checked?'Included':'Disabled']];
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
function syncRouterVersion(version){
 $('routerOsVersion').value=version;
 const badge=$('targetVersionBadge');if(badge)badge.textContent='RouterOS v'+version;
 const preview=$('platformVersionText');if(preview)preview.textContent='RouterOS v'+version;
 document.querySelectorAll('[data-router-version]').forEach(button=>{
  const active=button.dataset.routerVersion===version;button.classList.toggle('active',active);
  const icon=button.querySelector('i');if(icon)icon.className=active?'bi bi-check-circle-fill':'bi bi-circle';
 });
}
$('routerOsVersion').addEventListener('change',()=>syncRouterVersion($('routerOsVersion').value));
document.querySelectorAll('[data-router-version]').forEach(button=>button.addEventListener('click',()=>syncRouterVersion(button.dataset.routerVersion)));
document.querySelectorAll('[data-profile]').forEach(button=>button.addEventListener('click',()=>{
 document.querySelectorAll('[data-profile]').forEach(item=>item.classList.toggle('active',item===button));
}));
$('nextStep').addEventListener('click',()=>{if(current===panels.length-1){renderReview();return}if(validate(current))show(current+1)});
$('prevStep').addEventListener('click',()=>show(current-1));
document.querySelectorAll('input[name="wanType"],#enableDhcp,#enableVlan,#enableQueue,#enableBurst,#enableWifi,#enablePppoeServer,#enableHotspot,#enableFailover,#enableRemote').forEach(x=>x.addEventListener('change',syncConditional));
$('bridgeName').addEventListener('input',()=>{if($('vlanParent').options[0]){$('vlanParent').options[0].value=clean($('bridgeName').value);$('vlanParent').options[0].textContent=clean($('bridgeName').value)||'Bridge'}});
$('copyScript').addEventListener('click',async function(){if(!renderReview())return;try{await navigator.clipboard.writeText($('scriptOutput').textContent);const old=this.innerHTML;this.innerHTML='<i class="bi bi-check2"></i> Copied';this.classList.add('is-success');setTimeout(()=>{this.innerHTML=old;this.classList.remove('is-success')},1600)}catch(e){alert('Copy failed. Select the script manually.')}});
$('downloadScript').addEventListener('click',()=>{if(!renderReview())return;const blob=new Blob([$('scriptOutput').textContent],{type:'text/plain;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(clean($('identity').value)||'mikrotik-router').replace(/\s+/g,'-').toLowerCase()+'.rsc';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});

function executableCommands(script){
 return script.split('\n').map(x=>x.trim()).filter(x=>x&&!x.startsWith('#')&&!x.startsWith(':log'));
}
function renderCommandRows(script){
 const commands=executableCommands(script);const box=$('commandResults');if(!box)return;
 box.innerHTML=commands.map((cmd,i)=>{
  return '<div class="mtg-result-row"><span class="mtg-result-index">'+String(i+1).padStart(2,'0')+'</span><code class="mtg-result-command">'+escapeHtml(cmd)+'</code><span class="mtg-result-status success">Validated</span></div>';
 }).join('')||'<div class="mtg-result-empty">No executable commands generated.</div>';
}
function escapeHtml(value){const e=document.createElement('div');e.textContent=String(value||'');return e.innerHTML}

syncConditional();show(0);
})();
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
 setVisible('dhcpFields',$('enableDhcp').checked);setVisible('vlanFields',$('enableVlan').checked);setVisible('directLanFields',$('lanMode').value==='direct');setVisible('secondVlanFields',$('enableVlan').checked&&$('enableSecondVlan').checked);setVisible('queueFields',$('enableQueue').checked);
 setVisible('burstFields',$('enableQueue').checked&&$('enableBurst').checked);setVisible('wifiFields',$('enableWifi').checked);
 setVisible('pppoeServerFields',$('enablePppoeServer').checked);setVisible('pppoeVlanFields',$('enablePppoeServer').checked&&$('enablePppoeVlan').checked);setVisible('hotspotFields',$('enableHotspot').checked);setVisible('failoverFields',$('enableFailover').checked);setVisible('remoteFields',$('enableRemote').checked);setVisible('routingFields',$('enableRouting').checked);
 const bt=$('backupWanType').value;setVisible('backupStaticFields',$('enableFailover').checked&&bt==='static');setVisible('backupPppoeFields',$('enableFailover').checked&&bt==='pppoe');setVisible('backupDhcpFields',$('enableFailover').checked&&bt==='dhcp');
 const rm=$('routingMode').value;setVisible('staticRoutingFields',$('enableRouting').checked&&rm==='static');setVisible('ospfRoutingFields',$('enableRouting').checked&&rm==='ospf');setVisible('bgpRoutingFields',$('enableRouting').checked&&rm==='bgp');
}
function validate(panelIndex=current){
 const errors=[];document.querySelectorAll('.invalid').forEach(x=>x.classList.remove('invalid'));
 const add=(id,msg)=>{errors.push(msg);$(id)?.classList.add('invalid')};
 const name=clean($('identity').value);if(!name||!/^[A-Za-z0-9_. -]+$/.test(name))add('identity','Enter a valid router identity.');
 if(panelIndex>=1||panelIndex===7){
  if(wanType()==='static'){
   const wanAddress=clean($('wanIp').value),wanGateway=clean($('gateway').value);
   if(!cidr.test(wanAddress))add('wanIp','Enter WAN IP in CIDR format.');
   if(!ip.test(wanGateway))add('gateway','Enter a valid WAN gateway.');
   if(cidr.test(wanAddress)&&ip.test(wanGateway))staticLinkErrors(wanAddress,wanGateway,'Primary WAN').forEach(error=>add(error.field==='address'?'wanIp':'gateway',error.message));
  }
  if(wanType()==='pppoe'){if(!clean($('pppoeUser').value))add('pppoeUser','PPPoE username is required.');if(!clean($('pppoePass').value))add('pppoePass','PPPoE password is required.')}
 }
 if(panelIndex>=2||panelIndex===7){if($('lanMode').value==='bridge'&&!clean($('bridgeName').value))add('bridgeName','Bridge name is required.');if(!cidr.test(clean($('lanIp').value)))add('lanIp','Enter the LAN gateway in CIDR format.');if($('lanMode').value==='bridge'&&!selectedPorts().length)errors.push('Select at least one LAN bridge port.');const lanChosen=$('lanMode').value==='bridge'?selectedPorts():[$('directLanInterface').value];if(lanChosen.includes($('wanInterface').value))errors.push('Primary WAN interface cannot also be used as LAN.');if($('enableFailover').checked&&lanChosen.includes($('backupWan').value))errors.push('Backup WAN interface cannot also be used as LAN.')}
 if((panelIndex>=3||panelIndex===7)&&$('enableDhcp').checked){['poolStart','poolEnd'].forEach(id=>{if(!ip.test(clean($(id).value)))add(id,'Enter valid DHCP pool addresses.')});if(!cidr.test(clean($('dhcpNetwork').value)))add('dhcpNetwork','Enter DHCP network in CIDR format.')}
 if(panelIndex>=3||panelIndex===7){if(!ip.test(clean($('dns1').value)))add('dns1','Primary DNS is invalid.');if(clean($('dns2').value)&&!ip.test(clean($('dns2').value)))add('dns2','Secondary DNS is invalid.')}
 if((panelIndex>=4||panelIndex===7)&&$('enableVlan').checked){const id=+$('vlanId').value;if(id<1||id>4094)add('vlanId','VLAN ID must be 1–4094.');if(!cidr.test(clean($('vlanIp').value)))add('vlanIp','Enter VLAN gateway in CIDR format.');if($('enableVlanFiltering').checked&&!clean($('vlanTaggedPorts').value))add('vlanTaggedPorts','Enter at least one tagged trunk port.');if($('enableSecondVlan').checked){const second=+$('secondVlanId').value;if(second<1||second>4094||second===id)add('secondVlanId','Second VLAN ID must be unique and between 1–4094.');if(!cidr.test(clean($('secondVlanIp').value)))add('secondVlanIp','Enter second VLAN gateway in CIDR format.');}}
 if((panelIndex>=6||panelIndex===7)&&$('enableQueue').checked){
  if(!cidr.test(clean($('queueTarget').value)))add('queueTarget','Queue target must use CIDR format.');
  if($('enableBurst').checked&&(!clean($('burstLimit').value)||!clean($('burstThreshold').value)||!clean($('burstTime').value)))errors.push('Complete all burst settings.');
 }
 if((panelIndex>=6||panelIndex===7)&&$('enablePppoeServer').checked&&$('enablePppoeVlan').checked){const pv=+$('pppoeVlanId').value;if(pv<1||pv>4094)add('pppoeVlanId','PPPoE VLAN ID must be 1–4094.');}
 if((panelIndex>=6||panelIndex===7)&&$('enableWifi').checked){if(!clean($('wifiSsid').value))add('wifiSsid','Wi-Fi SSID is required.');if(clean($('wifiPassword').value).length<8)add('wifiPassword','Wi-Fi password must be at least 8 characters.');}
 if((panelIndex>=6||panelIndex===7)&&$('enableFailover').checked&&$('enableNetwatch').checked&&!ip.test(clean($('netwatchHost').value)))add('netwatchHost','Enter a valid Netwatch host IP.');
 if(panelIndex>=6||panelIndex===7){
  if($('enablePppoeServer').checked){if(!ip.test(clean($('pppoeLocal').value)))add('pppoeLocal','Enter a valid PPPoE local address.');if(!poolRangeValid($('pppoePool').value))add('pppoePool','PPPoE pool must be startIP-endIP.');if(!clean($('pppoeSecretUser').value))add('pppoeSecretUser','PPPoE test username is required.');if(!clean($('pppoeSecretPass').value))add('pppoeSecretPass','PPPoE test password is required.')}
  if($('enableHotspot').checked){if(!cidr.test(clean($('hotspotGateway').value)))add('hotspotGateway','Hotspot gateway must use CIDR format.');if(!poolRangeValid($('hotspotPool').value))add('hotspotPool','Hotspot pool must be startIP-endIP.');if(!clean($('hotspotDnsName').value))add('hotspotDnsName','Hotspot DNS name is required.');if(!clean($('hotspotUser').value))add('hotspotUser','Hotspot admin username is required.');if(!clean($('hotspotPass').value))add('hotspotPass','Hotspot admin password is required.')}
  if($('enableFailover').checked){const bt=$('backupWanType').value;if(bt==='static'){
    const backupAddress=clean($('backupIp').value),backupGateway=clean($('backupGateway').value);
    if(!cidr.test(backupAddress))add('backupIp','Enter backup IP in CIDR format.');
    if(!ip.test(backupGateway))add('backupGateway','Enter a valid backup gateway.');
    if(cidr.test(backupAddress)&&ip.test(backupGateway))staticLinkErrors(backupAddress,backupGateway,'Backup WAN').forEach(error=>add(error.field==='address'?'backupIp':'backupGateway',error.message));
   }if(bt==='pppoe'&&(!clean($('backupUser').value)||!clean($('backupPass').value)))errors.push('Backup PPPoE username and password are required.');const pd=+$('primaryDistance').value,bd=+$('backupDistance').value;if(pd<1||pd>250)add('primaryDistance','Primary distance must be 1–250.');if(bd<2||bd>250||bd<=pd)add('backupDistance','Backup distance must be greater than primary distance.');if($('backupWan').value===$('primaryWanPort').value)add('backupWan','Backup WAN must differ from primary WAN.');}
  if($('enableRemote').checked){if(!cidr.test(clean($('remoteSource').value)))add('remoteSource','Management source must use CIDR format.');const wp=+$('winboxPort').value;if(wp<1||wp>65535)add('winboxPort','Winbox port must be 1–65535.');}
  if($('enableRouting').checked){const rm=$('routingMode').value;if(rm==='static'){if(!cidr.test(clean($('staticRouteDestination').value)))add('staticRouteDestination','Static destination must use CIDR format.');if(!ip.test(clean($('staticRouteGateway').value)))add('staticRouteGateway','Enter a valid next-hop gateway.');}if(rm==='ospf'){if(!ip.test(clean($('ospfRouterId').value)))add('ospfRouterId','Enter a valid OSPF Router ID.');if(!cidr.test(clean($('ospfNetwork').value)))add('ospfNetwork','OSPF network must use CIDR format.');}if(rm==='bgp'){if(!ip.test(clean($('bgpRouterId').value)))add('bgpRouterId','Enter a valid BGP Router ID.');if(!ip.test(clean($('bgpNeighbor').value)))add('bgpNeighbor','Enter a valid BGP neighbor IP.');if(!cidr.test(clean($('bgpNetwork').value)))add('bgpNetwork','BGP network must use CIDR format.');}}
 }
 const box=$('validationSummary');box.hidden=!errors.length;box.innerHTML=errors.length?'<i class="bi bi-exclamation-triangle"></i><div><strong>Please fix:</strong><ul><li>'+errors.join('</li><li>')+'</li></ul></div>':'';
 return !errors.length;
}
function networkFromCidr(v){return clean(v).split('/')[0]}
function poolRangeValid(v){const p=clean(v).split('-');return p.length===2&&ip.test(p[0])&&ip.test(p[1])}
function gatewayAddress(v){return networkFromCidr(v)}
function ipv4Number(v){
 const parts=clean(v).split('.').map(Number);
 if(parts.length!==4||parts.some(n=>!Number.isInteger(n)||n<0||n>255))return null;
 return (((parts[0]<<24)>>>0)+(parts[1]<<16)+(parts[2]<<8)+parts[3])>>>0;
}
function cidrDetails(v){
 const parts=clean(v).split('/');
 if(parts.length!==2||!ip.test(parts[0]))return null;
 const prefix=Number(parts[1]);if(!Number.isInteger(prefix)||prefix<0||prefix>32)return null;
 const address=ipv4Number(parts[0]);
 const mask=prefix===0?0:(0xffffffff<<(32-prefix))>>>0;
 const network=(address&mask)>>>0;
 const broadcast=(network|(~mask>>>0))>>>0;
 return {address,prefix,mask,network,broadcast};
}
function staticLinkErrors(addressValue,gatewayValue,label){
 const result=[],details=cidrDetails(addressValue),gateway=ipv4Number(gatewayValue);
 if(!details||gateway===null)return result;
 if(details.prefix<31&&details.address===details.network)result.push({field:'address',message:label+' IP is the subnet network address and cannot be assigned to the router.'});
 if(details.prefix<31&&details.address===details.broadcast)result.push({field:'address',message:label+' IP is the subnet broadcast address and cannot be assigned to the router.'});
 if((gateway&details.mask)!==details.network)result.push({field:'gateway',message:label+' gateway must be inside the same subnet as the WAN IP.'});
 if(gateway===details.address)result.push({field:'gateway',message:label+' gateway cannot be the same as the router WAN IP.'});
 if(details.prefix<31&&(gateway===details.network||gateway===details.broadcast))result.push({field:'gateway',message:label+' gateway cannot be a network or broadcast address.'});
 return result;
}
function buildScript(){
 const lines=[];const wan=$('wanInterface').value;const bridge=clean($('bridgeName').value);const lanInterface=$('lanMode').value==='bridge'?bridge:$('directLanInterface').value;const w=wanType();
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
 if(w==='dhcp'){const distance=$('enableFailover').checked?' default-route-distance='+$('primaryDistance').value:'';lines.push('/ip dhcp-client add interface='+wan+' add-default-route=yes'+distance+' check-gateway=ping use-peer-dns=no disabled=no comment="PRIMARY ISP DHCP"');}
 if(w==='static'){
   lines.push('/ip address add address='+clean($('wanIp').value)+' interface='+wan+' comment="ISP STATIC"');
   const recursiveStaticFailover=$('enableFailover').checked&&$('backupWanType').value==='static';
   if(!recursiveStaticFailover){
    const routeOptions=$('enableFailover').checked?' distance='+$('primaryDistance').value+' check-gateway=ping':'';
    lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('gateway').value)+routeOptions+' comment="DEFAULT ROUTE"');
   }
  }
 if(w==='pppoe'){const mtu=$('pppoeMru').checked?' max-mtu=1480 max-mru=1480':'',distance=$('enableFailover').checked?' default-route-distance='+$('primaryDistance').value:'';lines.push('/interface pppoe-client add name=pppoe-out1 interface='+wan+' user='+q($('pppoeUser').value)+' password='+q($('pppoePass').value)+' add-default-route=yes'+distance+' use-peer-dns=no disabled=no'+mtu+' comment="PRIMARY ISP PPPOE"');}
 lines.push('');
 lines.push('# ---------- LAN DEPLOYMENT ----------');
 if($('lanMode').value==='bridge'){lines.push('/interface bridge add name='+bridge+' protocol-mode=rstp comment="LAN BRIDGE"');selectedPorts().forEach(p=>lines.push('/interface bridge port add bridge='+bridge+' interface='+p+' comment="LAN PORT"'));}else lines.push('# Direct-port LAN selected: no bridge will be created');
 lines.push('/ip address add address='+clean($('lanIp').value)+' interface='+lanInterface+' comment="LAN GATEWAY"');
 lines.push('');
 lines.push('# ---------- DNS ----------');
 const dns=[clean($('dns1').value),clean($('dns2').value)].filter(Boolean).join(',');
 lines.push('/ip dns set servers='+dns+' allow-remote-requests=yes');
 if($('enableDhcp').checked){
  lines.push('');
  lines.push('# ---------- DHCP SERVER ----------');
  lines.push('/ip pool add name=pool-LAN ranges='+clean($('poolStart').value)+'-'+clean($('poolEnd').value));
  lines.push('/ip dhcp-server add name=dhcp-LAN interface='+lanInterface+' address-pool=pool-LAN lease-time='+$('leaseTime').value+' disabled=no');
  lines.push('/ip dhcp-server network add address='+clean($('dhcpNetwork').value)+' gateway='+networkFromCidr($('lanIp').value)+' dns-server='+dns);
 }
 if($('enableVlan').checked){
  lines.push('');lines.push('# ---------- VLAN ----------');
  const vn=clean($('vlanName').value);lines.push('/interface vlan add name='+vn+' vlan-id='+$('vlanId').value+' interface='+clean($('vlanParent').value)+' comment="TAGGED VLAN"');
  lines.push('/ip address add address='+clean($('vlanIp').value)+' interface='+vn+' comment="VLAN GATEWAY"');
  if($('enableVlanFiltering').checked){const tagged=clean($('vlanTaggedPorts').value),access=$('vlanAccessPort').value,vid=$('vlanId').value;lines.push('/interface bridge port set [find interface='+access+'] pvid='+vid+' comment="VLAN '+vid+' ACCESS"');lines.push('/interface bridge vlan add bridge='+bridge+' vlan-ids='+vid+' tagged='+bridge+','+tagged+' untagged='+access+' comment="PRODUCTION VLAN '+vid+'"');lines.push('/interface bridge set [find name='+bridge+'] vlan-filtering=yes');}
  if($('enableSecondVlan').checked){const id2=$('secondVlanId').value,name2=clean($('secondVlanName').value),access2=$('secondVlanAccessPort').value;lines.push('/interface vlan add name='+name2+' vlan-id='+id2+' interface='+clean($('vlanParent').value)+' comment="SECOND ISP VLAN"');lines.push('/ip address add address='+clean($('secondVlanIp').value)+' interface='+name2+' comment="SECOND VLAN GATEWAY"');if($('enableVlanFiltering').checked){lines.push('/interface bridge port set [find interface='+access2+'] pvid='+id2);lines.push('/interface bridge vlan add bridge='+bridge+' vlan-ids='+id2+' tagged='+bridge+','+clean($('vlanTaggedPorts').value)+' untagged='+access2+' comment="SECOND PRODUCTION VLAN"');}}
 }
 if($('enableNat').checked){
  lines.push('');lines.push('# ---------- NAT FOR ALL ACTIVE WANS ----------');
  const out=w==='pppoe'?'pppoe-out1':wan;
  if(w==='static')lines.push('/ip firewall nat add chain=srcnat out-interface='+out+' action=src-nat to-addresses='+networkFromCidr($('wanIp').value)+' comment="PRIMARY STATIC WAN NAT"');
  else lines.push('/ip firewall nat add chain=srcnat out-interface='+out+' action=masquerade comment="PRIMARY DYNAMIC WAN NAT"');
  if($('enableFailover').checked){
   const backupType=$('backupWanType').value,backupOut=backupType==='pppoe'?'pppoe-backup':$('backupWan').value;
   if(backupType==='static')lines.push('/ip firewall nat add chain=srcnat out-interface='+backupOut+' action=src-nat to-addresses='+networkFromCidr($('backupIp').value)+' comment="BACKUP STATIC WAN NAT"');
   else lines.push('/ip firewall nat add chain=srcnat out-interface='+backupOut+' action=masquerade comment="BACKUP DYNAMIC WAN NAT"');
  }
 }
 if($('enableFirewall').checked){
  lines.push('');lines.push('# ---------- BASELINE FIREWALL ----------');
  if($('enableChainGuide').checked){lines.push('# INPUT = traffic addressed to the router');lines.push('# FORWARD = traffic passing through the router');lines.push('# OUTPUT = traffic created by the router');}
  lines.push('/ip firewall filter add chain=input action=accept connection-state=established,related,untracked comment="ACCEPT ESTABLISHED"');
  lines.push('/ip firewall filter add chain=input action=drop connection-state=invalid comment="DROP INVALID"');
  if($('enableIcmpProtection').checked){
   lines.push('/ip firewall filter add chain=input protocol=icmp limit=10,20:packet action=accept comment="LIMIT ICMP"');
   lines.push('/ip firewall filter add chain=input protocol=icmp action=drop comment="DROP ICMP FLOOD"');
  }else lines.push('/ip firewall filter add chain=input action=accept protocol=icmp comment="ALLOW ICMP"');
  lines.push('/ip firewall filter add chain=input action=accept in-interface='+lanInterface+' comment="ALLOW LAN MANAGEMENT"');
  if($('enablePortScanProtection').checked){
   lines.push('/ip firewall filter add chain=input protocol=tcp psd=21,3s,3,1 action=add-src-to-address-list address-list=port-scanners address-list-timeout=1d comment="DETECT PORT SCAN"');
   lines.push('/ip firewall filter add chain=input src-address-list=port-scanners action=drop comment="DROP PORT SCANNERS"');
  }
  if($('enableBogonProtection').checked){['0.0.0.0/8','10.0.0.0/8','100.64.0.0/10','127.0.0.0/8','169.254.0.0/16','172.16.0.0/12','192.0.0.0/24','192.168.0.0/16','224.0.0.0/3'].forEach(net=>lines.push('/ip firewall address-list add list=BOGONS address='+net+' comment="BOGON SOURCE"'));const bogonWan=w==='pppoe'?'pppoe-out1':wan;lines.push('/ip firewall filter add chain=input in-interface='+bogonWan+' src-address-list=BOGONS action=drop comment="DROP BOGON FROM WAN"');}
  if($('enableRemote').checked)lines.push('/ip firewall filter add chain=input action=accept protocol=tcp src-address='+clean($('remoteSource').value)+' dst-port=22,'+$('winboxPort').value+' comment="ALLOW RESTRICTED REMOTE MANAGEMENT"');
  const inIf=w==='pppoe'?'pppoe-out1':wan;
  lines.push('/ip firewall filter add chain=input action=drop in-interface='+inIf+' comment="DROP PRIMARY WAN INPUT"');
  if($('enableFailover').checked){
   const backupIn=$('backupWanType').value==='pppoe'?'pppoe-backup':$('backupWan').value;
   lines.push('/ip firewall filter add chain=input action=drop in-interface='+backupIn+' comment="DROP BACKUP WAN INPUT"');
  }
  lines.push('/ip firewall filter add chain=input action=drop comment="DROP OTHER ROUTER INPUT"');
  lines.push('/ip firewall filter add chain=forward action=accept connection-state=established,related,untracked comment="ACCEPT ESTABLISHED FORWARD"');
  lines.push('/ip firewall filter add chain=forward action=drop connection-state=invalid comment="DROP INVALID FORWARD"');
  lines.push('/ip firewall filter add chain=forward action=accept in-interface='+lanInterface+' comment="ALLOW LAN FORWARD"');
  lines.push('/ip firewall filter add chain=forward action=drop comment="DROP OTHER FORWARD"');
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
  let pppServerIf=clean($('pppoeServerInterface').value);if($('enablePppoeVlan').checked){pppServerIf='pppoe-vlan'+$('pppoeVlanId').value;lines.push('/interface vlan add name='+pppServerIf+' vlan-id='+$('pppoeVlanId').value+' interface='+$('pppoeVlanParent').value+' comment="PPPOE SUBSCRIBER VLAN"');}
  lines.push('/interface pppoe-server server add interface='+pppServerIf+' service-name='+q($('pppoeServiceName').value)+' default-profile=profile-PPPOE one-session-per-host=yes disabled=no');
  lines.push('/ppp secret add name='+q($('pppoeSecretUser').value)+' password='+q($('pppoeSecretPass').value)+' service=pppoe profile=profile-PPPOE');
 }
 if($('enableHotspot').checked){
  lines.push('');lines.push('# ---------- HOTSPOT ----------');
  const hsIf=$('hotspotWifiRedirect').checked&&$('enableWifi').checked?clean($('wifiBridge').value):clean($('hotspotInterface').value),hsGateway=clean($('hotspotGateway').value);
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
  const scenario=$('failoverScenario').value,primaryIf=$('primaryWanPort').value,backupIf=$('backupWan').value,backupType=$('backupWanType').value;
  lines.push('# Scenario: '+$('failoverScenario').selectedOptions[0].textContent);
  lines.push('# 5-port design: '+primaryIf+'=PRIMARY, '+backupIf+'=BACKUP, '+clean($('failoverLanPorts').value)+'=LAN');
  lines.push('/interface ethernet set [find default-name='+primaryIf+'] comment="PRIMARY WAN"');lines.push('/interface ethernet set [find default-name='+backupIf+'] comment="BACKUP WAN"');
  if(backupType==='dhcp')lines.push('/ip dhcp-client add interface='+backupIf+' add-default-route=yes default-route-distance='+$('backupDistance').value+' check-gateway=ping use-peer-dns=no comment="BACKUP DHCP WAN" disabled=no');
  if(backupType==='static'){
   lines.push('/ip address add address='+clean($('backupIp').value)+' interface='+backupIf+' comment="BACKUP STATIC WAN"');
   if(w==='static'){
    const primaryProbe=clean($('netwatchHost').value)||'1.1.1.1';
    const backupProbe=primaryProbe==='8.8.8.8'?'1.0.0.1':'8.8.8.8';
    lines.push('# Recursive routes test Internet reachability beyond each ISP gateway');
    lines.push('/ip route add dst-address='+primaryProbe+'/32 gateway='+clean($('gateway').value)+' scope=10 comment="PRIMARY INTERNET PROBE"');
    lines.push('/ip route add dst-address='+backupProbe+'/32 gateway='+clean($('backupGateway').value)+' scope=10 comment="BACKUP INTERNET PROBE"');
    lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+primaryProbe+' distance='+$('primaryDistance').value+' check-gateway=ping target-scope=11 comment="PRIMARY RECURSIVE DEFAULT"');
    lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+backupProbe+' distance='+$('backupDistance').value+' check-gateway=ping target-scope=11 comment="BACKUP RECURSIVE DEFAULT"');
   }else{
    lines.push('/ip route add dst-address=0.0.0.0/0 gateway='+clean($('backupGateway').value)+' distance='+$('backupDistance').value+' check-gateway=ping comment="BACKUP DEFAULT ROUTE"');
   }
  }
  if(backupType==='pppoe')lines.push('/interface pppoe-client add name=pppoe-backup interface='+backupIf+' user='+q($('backupUser').value)+' password='+q($('backupPass').value)+' add-default-route=yes default-route-distance='+$('backupDistance').value+' use-peer-dns=no disabled=no comment="BACKUP PPPOE WAN"');
  if($('enableNetwatch').checked){
   const monitorHost=clean($('netwatchHost').value);
   lines.push('# Netwatch provides status logs; route failover is handled by check-gateway');
   lines.push('/tool netwatch add host='+monitorHost+' interval='+$('netwatchInterval').value+' timeout=3s up-script=":log info PRIMARY-WAN-UP" down-script=":log warning PRIMARY-WAN-DOWN" comment="WAN STATUS MONITOR"');
  }
 }
 if($('enableRouting').checked){
  lines.push('');lines.push('# ---------- ROUTING GENERATOR ----------');const mode=$('routingMode').value,version=$('routerOsVersion').value;
  if(mode==='static')lines.push('/ip route add dst-address='+clean($('staticRouteDestination').value)+' gateway='+clean($('staticRouteGateway').value)+' distance='+$('staticRouteDistance').value+' comment="GENERATED STATIC ROUTE"');
  if(mode==='ospf'&&version==='7'){lines.push('/routing ospf instance add name=ospf-instance router-id='+clean($('ospfRouterId').value));lines.push('/routing ospf area add name=backbone area-id=0.0.0.0 instance=ospf-instance');lines.push('/routing ospf interface-template add area=backbone networks='+clean($('ospfNetwork').value));}
  if(mode==='ospf'&&version==='6'){lines.push('/routing ospf instance set [find default=yes] router-id='+clean($('ospfRouterId').value));lines.push('/routing ospf network add network='+clean($('ospfNetwork').value)+' area=backbone');}
  if(mode==='bgp'&&version==='7'){lines.push('/ip firewall address-list add list=bgp-networks address='+clean($('bgpNetwork').value));lines.push('/routing bgp template add name=bgp-template as='+$('bgpLocalAs').value+' router-id='+clean($('bgpRouterId').value));lines.push('/routing bgp connection add name=bgp-peer remote.address='+clean($('bgpNeighbor').value)+' remote.as='+$('bgpRemoteAs').value+' templates=bgp-template output.network=bgp-networks');}
  if(mode==='bgp'&&version==='6'){lines.push('/routing bgp instance set default as='+$('bgpLocalAs').value+' router-id='+clean($('bgpRouterId').value));lines.push('/routing bgp peer add name=bgp-peer remote-address='+clean($('bgpNeighbor').value)+' remote-as='+$('bgpRemoteAs').value);lines.push('/routing bgp network add network='+clean($('bgpNetwork').value));}
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
 if($('enableDiagnostics').checked){lines.push('');lines.push('# ---------- VERIFY & TROUBLESHOOT ----------');lines.push('/interface print terse');lines.push('/ip address print');lines.push('/ip route print');lines.push('/ip firewall filter print stats');if($('enablePppoeServer').checked)lines.push('/ppp active print');if($('enableHotspot').checked){lines.push('/ip hotspot active print');lines.push('/ip hotspot host print');}const target=clean($('diagnosticTarget').value);lines.push('/ping '+target+' count=4');lines.push('/tool traceroute '+target);}
 lines.push('');lines.push('# ---------- END ----------');lines.push(':log info "Hasan MikroTik generated configuration applied"');
 return lines.join('\n');
}
function renderReview(){
 if(!validate(7))return false;
 const script=buildScript();$('scriptOutput').textContent=script;$('lineCount').textContent=script.split('\n').filter(x=>x&& !x.startsWith('#')).length+' commands';renderCommandRows(script);
 $('topologyRouter').textContent=clean($('identity').value)||'Router';
 const values=[['RouterOS','v'+$('routerOsVersion').value],['WAN',wanType().toUpperCase()],['Uplink',$('wanInterface').value],['LAN',clean($('lanIp').value)],['LAN mode',$('lanMode').value==='bridge'?'Bridge / '+selectedPorts().join(', '):'Direct / '+$('directLanInterface').value],['DHCP',$('enableDhcp').checked?'Enabled':'Disabled'],['VLAN',$('enableVlan').checked?'VLAN '+$('vlanId').value+($('enableVlanFiltering').checked?' / Production':' / Interface'):'Disabled'],['Firewall',$('enableFirewall').checked?'Baseline'+($('enableBogonProtection').checked?' + Bogon':''):'Disabled'],['Queue',$('enableQueue').checked?$('queueMode').value+' / '+clean($('queueTarget').value):'Disabled'],['Wi-Fi',$('enableWifi').checked?clean($('wifiSsid').value):'Disabled'],['PPPoE Server',$('enablePppoeServer').checked?'Enabled':'Disabled'],['Hotspot',$('enableHotspot').checked?'Enabled':'Disabled'],['Failover',$('enableFailover').checked?$('failoverScenario').selectedOptions[0].textContent:'Disabled'],['Remote',$('enableRemote').checked?$('remoteMode').value+' / '+clean($('remoteSource').value):'Disabled'],['Routing',$('enableRouting').checked?$('routingMode').value.toUpperCase():'Disabled'],['Diagnostics',$('enableDiagnostics').checked?'Included':'Disabled']];
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
function syncFailoverPorts(){
 const primary=$('primaryWanPort').value,backup=$('backupWan').value;
 document.querySelectorAll('#lanPorts input').forEach(port=>{
  if(port.value===primary||port.value===backup)port.checked=false;
  else if(['ether3','ether4','ether5'].includes(port.value))port.checked=true;
 });
 const activeLan=selectedPorts();
 $('failoverLanPorts').value=activeLan.length?activeLan.join(','):'Select LAN ports';
}
function syncFailoverScenario(){
 const map={
  static_static:['static','static'],
  static_dhcp:['static','dhcp'],
  static_pppoe:['static','pppoe'],
  dhcp_static:['dhcp','static'],
  dhcp_dhcp:['dhcp','dhcp'],
  dhcp_pppoe:['dhcp','pppoe'],
  pppoe_static:['pppoe','static'],
  pppoe_dhcp:['pppoe','dhcp'],
  pppoe_pppoe:['pppoe','pppoe']
 };
 const pair=map[$('failoverScenario').value]||map.static_static;
 const radio=document.querySelector('input[name="wanType"][value="'+pair[0]+'"]');if(radio)radio.checked=true;
 $('backupWanType').value=pair[1];
 $('wanInterface').value=$('primaryWanPort').value;
 syncFailoverPorts();
 syncConditional();
}
$('failoverScenario').addEventListener('change',syncFailoverScenario);
$('backupWan').addEventListener('change',()=>{syncFailoverPorts();syncConditional()});
$('primaryWanPort').addEventListener('change',()=>{$('wanInterface').value=$('primaryWanPort').value;syncFailoverPorts()});
$('wanInterface').addEventListener('change',()=>{if([...$('primaryWanPort').options].some(o=>o.value===$('wanInterface').value)){$('primaryWanPort').value=$('wanInterface').value;syncFailoverPorts()}});
document.querySelectorAll('#lanPorts input').forEach(port=>port.addEventListener('change',()=>{$('failoverLanPorts').value=selectedPorts().join(',')}));
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
document.querySelectorAll('input[name="wanType"],#lanMode,#enableDhcp,#enableVlan,#enableSecondVlan,#enableQueue,#enableBurst,#enableWifi,#enablePppoeServer,#enablePppoeVlan,#enableHotspot,#enableFailover,#backupWanType,#enableRemote,#enableRouting,#routingMode').forEach(x=>x.addEventListener('change',syncConditional));
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

syncFailoverScenario();syncConditional();show(0);
})();
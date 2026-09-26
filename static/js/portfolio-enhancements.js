(function(){
'use strict';

function ready(fn){if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',fn)}else{fn()}}
function el(tag,className,html){var node=document.createElement(tag);if(className)node.className=className;if(html!==undefined)node.innerHTML=html;return node}

ready(function(){
  var about=document.querySelector('#about .container');
  if(about&&!about.querySelector('.about-profile-grid')){
    var profile=el('div','about-profile-grid portfolio-upgrades',
      '<article class="profile-mini-card"><div class="profile-mini-head"><span class="profile-mini-icon"><i class="bi bi-translate"></i></span>LANGUAGES</div><div class="profile-chip-list"><span class="profile-chip">Bengali <small>Native</small></span><span class="profile-chip">English <small>Intermediate</small></span><span class="profile-chip">German <small>Learning</small></span></div></article>'+
      '<article class="profile-mini-card"><div class="profile-mini-head"><span class="profile-mini-icon"><i class="bi bi-stars"></i></span>INTERESTS</div><div class="profile-chip-list"><span class="profile-chip">Network Operations</span><span class="profile-chip">AI Automation</span><span class="profile-chip">ML Research</span><span class="profile-chip">Competitive Programming</span></div></article>');
    about.appendChild(profile);
  }

  var levels={'Cisco':'Intermediate','MikroTik':'Advanced','Huawei':'Intermediate','Juniper':'Learning','OLT':'Advanced','Linux':'Intermediate','Python':'Advanced','Django':'Intermediate','Wireshark':'Intermediate','Zabbix':'Intermediate','PRTG Network Monitor':'Intermediate','SNMP':'Intermediate'};
  document.querySelectorAll('#technology .tech-item').forEach(function(item){
    var name=(item.querySelector('span')||{}).textContent;
    name=name?name.trim():'';
    if(levels[name]&&!item.querySelector('.skill-level')){
      var level=el('div','skill-level','<span>'+levels[name]+'</span>');
      item.appendChild(level);
    }
  });

  document.querySelectorAll('#experience .experience-list').forEach(function(list,index){
    var items=list.querySelectorAll('li');
    if(items.length<=3||list.dataset.enhanced)return;
    list.dataset.enhanced='true';
    list.classList.add('is-collapsed');
    var hidden=items.length-3;
    var button=el('button','experience-toggle','<span>View '+hidden+' more responsibilities</span><i class="bi bi-chevron-down"></i>');
    button.type='button';button.setAttribute('aria-expanded','false');
    button.addEventListener('click',function(){
      var expanded=button.getAttribute('aria-expanded')==='true';
      button.setAttribute('aria-expanded',String(!expanded));
      list.classList.toggle('is-collapsed',expanded);
      button.querySelector('span').textContent=expanded?'View '+hidden+' more responsibilities':'Show less';
    });
    list.insertAdjacentElement('afterend',button);
  });

  var projectVisuals=[
    ['bi-shield-lock','bi-router','Architecture concept'],
    ['bi-activity','bi-speedometer2','Operational workflow'],
    ['bi-hdd-network','bi-diagram-3','Troubleshooting workflow'],
    ['bi-code-slash','bi-window','Live portfolio'],
    ['bi-router','bi-terminal','Live tool']
  ];
  document.querySelectorAll('#projects .project-card').forEach(function(card,index){
    if(card.dataset.enhanced)return;card.dataset.enhanced='true';
    var h3=card.querySelector('h3');
    var iconA=(projectVisuals[index]||projectVisuals[0])[0],iconB=(projectVisuals[index]||projectVisuals[0])[1];
    var visual=el('div','project-visual','<i class="bi '+iconA+'"></i><span class="project-flow-line"></span><i class="bi '+iconB+'"></i>');
    var projectIcon=card.querySelector('.project-icon');
    if(projectIcon)projectIcon.insertAdjacentElement('afterend',visual);
    var tags=card.querySelector('.project-tags');
    var existingMeta=card.querySelector('.project-meta');
    if(!existingMeta){
      var meta=el('div','project-meta');
      var status=el('span','project-status',(projectVisuals[index]||projectVisuals[0])[2]);
      var action;
      if(h3&&h3.textContent.indexOf('Django Portfolio')>-1){
        action=el('a','project-action','View repository <i class="bi bi-github"></i>');
        action.href='https://github.com/Hasan-Gazi-1617/personal-portfolio';action.target='_blank';action.rel='noopener noreferrer';
      }else{
        action=el('span','project-action','Project overview <i class="bi bi-arrow-up-right"></i>');
      }
      meta.append(status,action);
      if(tags)tags.insertAdjacentElement('afterend',meta);else card.appendChild(meta);
    }
  });

  document.querySelectorAll('.certifications-section .certification-card').forEach(function(card){
    if(!card.querySelector('.cert-status'))card.querySelector('div:last-child').appendChild(el('span','cert-status','<i class="bi bi-arrow-repeat"></i> Continuous learning'));
  });

  var cvLink=document.querySelector('.hero-buttons a[download]');
  if(cvLink&&!document.querySelector('.cv-preview-trigger')){
    var preview=el('button','btn btn-secondary-custom cv-preview-trigger','Preview CV <i class="bi bi-file-earmark-person"></i>');
    preview.type='button';cvLink.insertAdjacentElement('afterend',preview);
    var modal=el('div','cv-modal');
    modal.id='cvPreviewModal';modal.setAttribute('aria-hidden','true');
    modal.innerHTML='<div class="cv-dialog" role="dialog" aria-modal="true" aria-labelledby="cvModalTitle"><div class="cv-dialog-head"><strong id="cvModalTitle"><i class="bi bi-file-earmark-person"></i> MD. HASAN — CV Preview</strong><button class="modal-icon-btn" type="button" aria-label="Close CV preview"><i class="bi bi-x-lg"></i></button></div><iframe class="cv-frame" title="MD. Hasan CV preview" loading="lazy"></iframe></div>';
    document.body.appendChild(modal);
    var frame=modal.querySelector('iframe'),close=modal.querySelector('button');
    function openCv(){frame.src=cvLink.href;modal.classList.add('is-open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';close.focus()}
    function closeCv(){modal.classList.remove('is-open');modal.setAttribute('aria-hidden','true');frame.removeAttribute('src');document.body.style.overflow=''}
    preview.addEventListener('click',openCv);close.addEventListener('click',closeCv);modal.addEventListener('click',function(e){if(e.target===modal)closeCv()});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('is-open'))closeCv()});
  }

  var contactLeft=document.querySelector('#contact .col-lg-7');
  if(contactLeft&&!contactLeft.querySelector('.contact-form-enhanced')){
    var label=contactLeft.querySelector('.section-label');
    if(label)label.insertAdjacentElement('beforebegin',el('span','contact-availability','AVAILABLE FOR NETWORKING OPPORTUNITIES'));
    var form=el('form','contact-form-enhanced');
    form.innerHTML='<div class="contact-form-row"><input name="name" type="text" placeholder="Your name" aria-label="Your name" required><input name="email" type="email" placeholder="Your email" aria-label="Your email" required></div><input name="subject" type="text" placeholder="Subject" aria-label="Subject" required><textarea name="message" placeholder="Write your message..." aria-label="Message" required></textarea><button class="btn btn-primary-custom contact-form-submit" type="submit">Compose Email <i class="bi bi-send"></i></button><small class="contact-form-note">Your email application will open with this message. No information is stored on the website.</small>';
    form.addEventListener('submit',function(e){
      e.preventDefault();var data=new FormData(form);
      var subject=encodeURIComponent(data.get('subject')||'Portfolio contact');
      var body=encodeURIComponent('Name: '+data.get('name')+'\nEmail: '+data.get('email')+'\n\n'+data.get('message'));
      window.location.href='mailto:mdhasan.cse9243@gmail.com?subject='+subject+'&body='+body;
    });
    contactLeft.appendChild(form);
  }

  var navLinks=Array.from(document.querySelectorAll('.navbar-custom .nav-link[href*="#"]')).filter(function(link){return link.hash&&document.querySelector(link.hash)});
  var sections=navLinks.map(function(link){return document.querySelector(link.hash)}).filter(Boolean);
  var lockedSection='',lockUntil=0,scrollTick=false;
  function setActiveSection(id){
    navLinks.forEach(function(link){
      var active=link.hash==='#'+id;
      link.classList.toggle('active',active);
      if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');
    });
  }
  function updateActiveSection(){
    scrollTick=false;
    if(lockedSection&&Date.now()<lockUntil){setActiveSection(lockedSection);return}
    lockedSection='';
    var marker=(document.querySelector('.navbar-custom')||{}).offsetHeight||82;
    marker+=90;
    var current=sections[0];
    sections.forEach(function(section){if(section.getBoundingClientRect().top<=marker)current=section});
    if((window.innerHeight+window.scrollY)>=document.documentElement.scrollHeight-8)current=sections[sections.length-1];
    if(current)setActiveSection(current.id);
  }
  navLinks.forEach(function(link){
    link.addEventListener('click',function(){
      lockedSection=link.hash.slice(1);lockUntil=Date.now()+1100;setActiveSection(lockedSection);
      window.setTimeout(updateActiveSection,1150);
    });
  });
  window.addEventListener('scroll',function(){if(!scrollTick){scrollTick=true;window.requestAnimationFrame(updateActiveSection)}},{passive:true});
  window.addEventListener('resize',updateActiveSection);
  updateActiveSection();

  if(!document.querySelector('.command-palette')){
    var launcher=el('button','command-launcher','<i class="bi bi-command"></i><kbd>Ctrl K</kbd>');
    launcher.type='button';launcher.setAttribute('aria-label','Open quick navigation');
    var palette=el('div','command-palette');palette.setAttribute('aria-hidden','true');
    palette.innerHTML='<div class="command-dialog" role="dialog" aria-modal="true" aria-label="Quick navigation"><div class="command-search-wrap"><i class="bi bi-search"></i><input class="command-search" type="search" placeholder="Search sections and actions..." autocomplete="off"></div><div class="command-results"></div><div class="command-hint"><span>↑↓ Navigate · Enter Open</span><span>Esc Close</span></div></div>';
    document.body.append(launcher,palette);
    var input=palette.querySelector('.command-search'),results=palette.querySelector('.command-results'),active=0;
    var adminLink=document.querySelector('.admin-view-link');
    var commands=[
      {label:'Go to About',detail:'Profile, languages and interests',icon:'bi-person',url:'#about'},
      {label:'View Expertise',detail:'Core networking capabilities',icon:'bi-diagram-3',url:'#expertise'},
      {label:'Explore Technology',detail:'Tools and proficiency levels',icon:'bi-cpu',url:'#technology'},
      {label:'Open Experience',detail:'Career timeline',icon:'bi-briefcase',url:'#experience'},
      {label:'View Projects',detail:'Featured technical work',icon:'bi-grid',url:'#projects'},
      {label:'Browse Lessons',detail:'Technical learning resources',icon:'bi-journal-code',url:'#lessons'},
      {label:'Contact Hasan',detail:'Email, LinkedIn and GitHub',icon:'bi-envelope',url:'#contact'},
      {label:'Download CV',detail:'PDF résumé',icon:'bi-download',url:cvLink?cvLink.href:'',download:true}
    ];
    if(adminLink)commands.push({label:'Admin View',detail:'Private owner access',icon:'bi-shield-lock',url:adminLink.href});
    function filtered(){var q=input.value.trim().toLowerCase();return commands.filter(function(cmd){return (cmd.label+' '+cmd.detail).toLowerCase().indexOf(q)>-1})}
    function render(){var list=filtered();if(active>=list.length)active=0;results.innerHTML=list.length?list.map(function(cmd,i){return '<button class="command-item '+(i===active?'is-active':'')+'" type="button" data-index="'+i+'"><i class="bi '+cmd.icon+'"></i><div><span>'+cmd.label+'</span><small>'+cmd.detail+'</small></div></button>'}).join(''):'<div class="command-empty">No matching action found.</div>';results.querySelectorAll('.command-item').forEach(function(btn){btn.addEventListener('click',function(){run(list[Number(btn.dataset.index)])})})}
    function run(cmd){if(!cmd)return;closePalette();if(cmd.download){var a=document.createElement('a');a.href=cmd.url;a.download='';a.click()}else if(cmd.url.charAt(0)==='#'){document.querySelector(cmd.url).scrollIntoView({behavior:'smooth'})}else{window.location.href=cmd.url}}
    function openPalette(){palette.classList.add('is-open');palette.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';input.value='';active=0;render();setTimeout(function(){input.focus()},30)}
    function closePalette(){palette.classList.remove('is-open');palette.setAttribute('aria-hidden','true');document.body.style.overflow=''}
    launcher.addEventListener('click',openPalette);palette.addEventListener('click',function(e){if(e.target===palette)closePalette()});input.addEventListener('input',function(){active=0;render()});input.addEventListener('keydown',function(e){var list=filtered();if(e.key==='ArrowDown'){e.preventDefault();active=(active+1)%list.length;render()}else if(e.key==='ArrowUp'){e.preventDefault();active=(active-1+list.length)%list.length;render()}else if(e.key==='Enter'){e.preventDefault();run(list[active])}});
    document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();palette.classList.contains('is-open')?closePalette():openPalette()}else if(e.key==='Escape'&&palette.classList.contains('is-open'))closePalette()});
  }
});
})();
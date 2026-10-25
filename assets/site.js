document.querySelectorAll('.copy').forEach(function(b){
  b.addEventListener('click',function(){
    var el=document.getElementById(b.dataset.copy),txt=el.textContent.trim(),label=b.textContent;
    function done(m){b.textContent=m;setTimeout(function(){b.textContent=label},1800)}
    function sel(){var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);done('Sélectionné, faites Copier')}
    try{navigator.clipboard.writeText(txt).then(function(){done('Copié')},sel)}catch(e){sel()}
  });
});

// Bandeau cookies : la balise Google Ads n'est chargée qu'après « Accepter ». Choix conservé 6 mois.
(function(){
  var box=document.getElementById('consent');
  if(!box)return;
  var KEY='brb-consent', MAX=1000*60*60*24*182;
  function lire(){try{var v=JSON.parse(localStorage.getItem(KEY));return v&&Date.now()-v.t<MAX?v.choix:null}catch(e){return null}}
  function charger(){
    gtag('consent','update',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted'});
    if(document.getElementById('gtag-js'))return;
    var s=document.createElement('script');s.async=true;s.id='gtag-js';
    s.src='https://www.googletagmanager.com/gtag/js?id='+box.dataset.gtag;
    document.head.appendChild(s);
  }
  function choisir(c){
    try{localStorage.setItem(KEY,JSON.stringify({choix:c,t:Date.now()}))}catch(e){}
    box.hidden=true;
    if(c==='granted')charger();
    else if(document.getElementById('gtag-js'))location.reload();
  }
  box.querySelectorAll('[data-consent]').forEach(function(b){b.addEventListener('click',function(){choisir(b.dataset.consent)})});
  document.querySelectorAll('[data-cookies]').forEach(function(b){b.addEventListener('click',function(){box.hidden=false})});
  var c=lire();
  if(c==='granted')charger();else if(!c)box.hidden=false;
})();

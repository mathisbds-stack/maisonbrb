document.querySelectorAll('.copy').forEach(function(b){
  b.addEventListener('click',function(){
    var el=document.getElementById(b.dataset.copy),txt=el.textContent.trim(),label=b.textContent;
    function done(m){b.textContent=m;setTimeout(function(){b.textContent=label},1800)}
    function sel(){var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);done('Sélectionné, faites Copier')}
    try{navigator.clipboard.writeText(txt).then(function(){done('Copié')},sel)}catch(e){sel()}
  });
});

path = r'boaapp\templates\boaapp\nfl_draft.html'
with open(path, 'a', encoding='utf-8') as f:
  f.write(r'''{% block extra_js %}
<script>
(function(){'use strict';

/* ══════════════════════════════════════════════════════════════
   7-IDEATIONS NAV + ELI5 + CLASSROOM STATE
   ══════════════════════════════════════════════════════════════ */
var ndClsCurrent=0,ndClsTotal=6,ndEli5Selected=null;

var ELI5_STRATS={
  casual:{QB:.7,RB:1.55,WR:.85,TE:.6,K:.3,DST:.3,name:'Robust RB'},
  analyst:{QB:1.0,RB:1.0,WR:1.0,TE:1.0,K:.5,DST:.5,name:'Balanced BPA'},
  zerorb:{QB:.7,RB:.45,WR:1.5,TE:1.15,K:.3,DST:.3,name:'Zero RB'},
  contrarian:{QB:1.15,RB:.85,WR:.85,TE:1.25,K:.4,DST:.4,name:'Contrarian'}
};

function ndSetMode(mode){
  document.querySelectorAll('.nd-mode-btn').forEach(function(b){
    b.classList.toggle('active',b.dataset.mode===mode);
  });
  document.querySelectorAll('.nd-pane').forEach(function(p){
    p.classList.toggle('active',p.dataset.pane===mode);
  });
}

function ndSelectPersona(key){
  ndEli5Selected=key;
  document.querySelectorAll('.nd-persona').forEach(function(el){
    el.classList.remove('selected');
  });
  var el=document.getElementById('nd-persona-'+key);
  if(el)el.classList.add('selected');
  var btn=document.getElementById('nd-eli5-run');
  if(btn)btn.disabled=false;
  var res=document.getElementById('nd-eli5-result');
  if(res)res.style.display='none';
}

function ndRunELI5(){
  if(!ndEli5Selected||typeof RAW==='undefined')return;
  var strat=ELI5_STRATS[ndEli5Selected];
  var weights={QB:strat.QB,RB:strat.RB,WR:strat.WR,TE:strat.TE,K:strat.K,DST:strat.DST};
  var pool=RAW.slice(0,80).map(function(r,idx){
    return{name:r[0],pos:r[1],team:r[2],bye:r[3],adp:r[4],rankScore:80-idx};
  });
  var avail=pool.slice();
  var drafted=[];
  var posNeeds={QB:1,RB:3,WR:3,TE:1,K:1,DST:1};
  var posHave={QB:0,RB:0,WR:0,TE:0,K:0,DST:0};
  for(var rnd=1;rnd<=8;rnd++){
    var best=null,bestScore=-Infinity,bestIdx=-1;
    for(var i=0;i<avail.length;i++){
      var p=avail[i];
      var w=weights[p.pos]||0.5;
      var score=p.rankScore*w;
      if((posHave[p.pos]||0)<(posNeeds[p.pos]||1))score*=1.15;
      else score*=0.35;
      score*=(0.92+Math.random()*0.16);
      if(score>bestScore){best=p;bestScore=score;bestIdx=i;}
    }
    if(!best)break;
    drafted.push({round:rnd,player:best});
    posHave[best.pos]=(posHave[best.pos]||0)+1;
    avail.splice(bestIdx,1);
  }
  var totalW=0;
  drafted.forEach(function(d){totalW+=weights[d.player.pos]||0.5;});
  var avg=drafted.length>0?totalW/drafted.length:0;
  var grade=avg>=1.1?'A+':avg>=0.95?'A':avg>=0.8?'B+':avg>=0.65?'B':'C';
  var posColors={QB:'#dc2626',RB:'#2563eb',WR:'#7c3aed',TE:'#059669',K:'#ca8a04',DST:'#e11d48'};
  var html='<div class="nd-eli5-picks">';
  drafted.forEach(function(d){
    var c=posColors[d.player.pos]||'#64748b';
    html+='<div class="nd-eli5-pick">'
      +'<div class="rnd">R'+d.round+'</div>'
      +'<div class="info">'
      +'<div class="name">'+d.player.name+'</div>'
      +'<div class="meta" style="color:'+c+';font-weight:700">'+d.player.pos
        +' <span style="color:var(--nd-muted);font-weight:400">&middot; '+d.player.team+'</span></div>'
      +'</div></div>';
  });
  html+='</div>';
  html+='<div class="nd-eli5-grade-card">'
    +'<div class="nd-eli5-grade-circle">'+grade+'</div>'
    +'<div><div style="font-size:.88rem;font-weight:800;color:var(--nd-text)">Draft Grade: '+grade+'</div>'
    +'<div style="font-size:.73rem;color:var(--nd-muted);margin:.2rem 0 .1rem">Strategy: <strong>'+strat.name+'</strong></div>'
    +'<div style="font-size:.68rem;color:var(--nd-muted)">Top 8 VOR-weighted picks for your archetype</div>'
    +'</div></div>';
  var result=document.getElementById('nd-eli5-result');
  result.innerHTML=html;
  result.style.display='block';
}

/* ── Classroom Carousel ── */
function ndClsShowSlide(n){
  ndClsCurrent=((n%ndClsTotal)+ndClsTotal)%ndClsTotal;
  document.querySelectorAll('.nd-cls-slide').forEach(function(el,i){
    el.classList.toggle('active',i===ndClsCurrent);
  });
  document.querySelectorAll('.nd-cls-dot').forEach(function(el,i){
    el.classList.toggle('active',i===ndClsCurrent);
  });
}
function ndClsNext(){ndClsShowSlide(ndClsCurrent+1);}
function ndClsPrev(){ndClsShowSlide(ndClsCurrent-1);}
function ndGotoClsDot(n){ndClsShowSlide(n);}

/* ── Share ── */
function ndShareDemo(){
  var url=window.location.href;
  if(navigator.share){navigator.share({title:'NFL Fantasy Draft Analytics',url:url});}
  else if(navigator.clipboard){
    navigator.clipboard.writeText(url);
    var btn=document.getElementById('ndShareBtn');
    if(btn){var orig=btn.innerHTML;btn.innerHTML='<i class="fas fa-check me-1"></i> Link Copied!';
      setTimeout(function(){btn.innerHTML=orig;},2200);}
  }
}

/* ── Scroll Spy + Progress Bar ── */
function ndInitNav(){
  var fill=document.getElementById('ndProgressFill');
  var navItems=document.querySelectorAll('.nd-nav-item[data-nav]');
  var sections=['nd-story','nd-demo','nd-classroom','nd-keypoints','nd-code','nd-about'];

  function onScroll(){
    var scrollTop=window.scrollY||document.documentElement.scrollTop;
    var docH=document.documentElement.scrollHeight-window.innerHeight;
    if(docH>0&&fill)fill.style.width=Math.min(100,(scrollTop/docH*100))+'%';

    var active=sections[0];
    for(var i=0;i<sections.length;i++){
      var el=document.getElementById(sections[i]);
      if(el&&el.getBoundingClientRect().top<=80){active=sections[i];}
    }
    navItems.forEach(function(item){
      item.classList.toggle('active',item.dataset.nav===active);
    });
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
}

/* ── Window exports (used in onclick="" attributes) ── */
window.ndSetMode=ndSetMode;
window.ndSelectPersona=ndSelectPersona;
window.ndRunELI5=ndRunELI5;
window.ndClsNext=ndClsNext;
window.ndClsPrev=ndClsPrev;
window.ndGotoClsDot=ndGotoClsDot;
window.ndShareDemo=ndShareDemo;

/* ══════════════════════════════════════════════════════════════
   ORIGINAL DRAFT ROOM ENGINE (verbatim from production build)
   ══════════════════════════════════════════════════════════════ */
''')

# Append the original IIFE inner content from the saved temp file
with open('nfl_orig_inner.tmp', 'r', encoding='utf-8') as tmp:
    with open(path, 'a', encoding='utf-8') as f:
        f.write(tmp.read())

# Close out the script block
with open(path, 'a', encoding='utf-8') as f:
    f.write(r'''
  /* ── Init navigation ── */
  ndInitNav();

})();
</script>
{% endblock %}
''')

print("nfl3 done: script block closed.")

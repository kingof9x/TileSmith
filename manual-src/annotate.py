# Circles (rounded boxes) and arrows for instruction screenshots (README and manual).
# Call  await annotate(pg, items)  right before the screenshot.
# Each item: {"sel": css selector} or {"text": start of the element's text} (optionally "within": css selector to search in),
# "n": the step number shown in the badge, "dx"/"dy": where the badge sits relative to the circle (pixels),
# "pad": extra space around the element, "all": true to circle every match of "sel" together,
# "side": "right"/"left" puts the badge just outside the box on that side ("gap" pixels away). The overlay is removed again with  await pg.evaluate(ANNOT_CLEAR).
ANNOT = r"""(items)=>{
 document.getElementById('tsAnnot')?.remove();
 const NS='http://www.w3.org/2000/svg',W=innerWidth,H=innerHeight;
 const svg=document.createElementNS(NS,'svg');svg.id='tsAnnot';svg.setAttribute('width',W);svg.setAttribute('height',H);
 svg.style.cssText='position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none';
 const mk=(t,a)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);svg.appendChild(e);return e};
 const defs=mk('defs',{});const m=document.createElementNS(NS,'marker');
 for(const [k,v] of Object.entries({id:'tsArr',viewBox:'0 0 10 10',refX:'8',refY:'5',markerWidth:'5',markerHeight:'5',orient:'auto-start-reverse'}))m.setAttribute(k,v);
 const p=document.createElementNS(NS,'path');p.setAttribute('d','M0,0 L10,5 L0,10 z');p.setAttribute('fill','#ff3b30');m.appendChild(p);defs.appendChild(m);
 const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!='hidden'};
 const find=it=>{const root=it.within?document.querySelector(it.within):document;if(!root)return null;
  if(it.sel){const a=[...root.querySelectorAll(it.sel)].filter(vis);if(!a.length)return null;if(!it.all)return a[0];
   const R=a.map(e=>e.getBoundingClientRect()),l=Math.min(...R.map(r=>r.left)),t=Math.min(...R.map(r=>r.top));
   return {getBoundingClientRect:()=>({left:l,top:t,width:Math.max(...R.map(r=>r.right))-l,height:Math.max(...R.map(r=>r.bottom))-t})}}
  const c=[...root.querySelectorAll('*')].filter(e=>vis(e)&&(e.textContent||'').trim().startsWith(it.text));
  return c.find(e=>![...e.children].some(k=>c.includes(k)))||null};
 const miss=[];
 for(const it of items){const e=find(it);if(!e){miss.push(it.text||it.sel);continue}
  const r=e.getBoundingClientRect(),pd=it.pad??8,cx=r.left+r.width/2,cy=r.top+r.height/2,rx=r.width/2+pd,ry=r.height/2+pd;
  mk('rect',{x:cx-rx,y:cy-ry,width:2*rx,height:2*ry,rx:Math.min(14,ry),fill:'none',stroke:'#ff3b30','stroke-width':4});
  if(it.n==null)continue;
  const ox=it.side=='right'?rx+(it.gap??42):it.side=='left'?-(rx+(it.gap??42)):(it.dx??-(rx+60));
  const bx=Math.max(18,Math.min(W-18,cx+ox)),by=Math.max(18,Math.min(H-18,cy+(it.dy??0)));
  const ang=Math.atan2(cy-by,cx-bx),c=Math.abs(Math.cos(ang)),sn=Math.abs(Math.sin(ang)),k=Math.min(c?rx/c:1e9,sn?ry/sn:1e9)+4,ex=cx-Math.cos(ang)*k,ey=cy-Math.sin(ang)*k;
  const sx=bx+Math.cos(ang)*18,sy=by+Math.sin(ang)*18;
  if(Math.hypot(ex-sx,ey-sy)>8)mk('line',{x1:sx,y1:sy,x2:ex,y2:ey,stroke:'#ff3b30','stroke-width':4,'marker-end':'url(#tsArr)'});
  mk('circle',{cx:bx,cy:by,r:16,fill:'#ff3b30',stroke:'#fff','stroke-width':2.5});
  const t=mk('text',{x:bx,y:by+6.5,'text-anchor':'middle','font-family':'Arial,Helvetica,sans-serif','font-size':19,'font-weight':'bold',fill:'#fff'});t.textContent=String(it.n)}
 document.body.appendChild(svg);return miss}"""
ANNOT_CLEAR = "()=>document.getElementById('tsAnnot')?.remove()"


async def annotate(pg, items):
    """Draw the circles and arrows; fail loudly if a target is missing so a renamed control is noticed."""
    miss = await pg.evaluate(ANNOT, items)
    assert not miss, f'annotation targets not found: {miss}'

(async()=>{const R={};const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 await new Promise(r=>{require('electron').ipcRenderer.invoke('ts-displays').then(d=>{R.displays=d.length;window.__D=d;r()})});
 // output window on the only display
 try{DISP=window.__D;const c=CVS[cc];outOpen(c,String(DISP[0].id));await sleep(1500);const o=OUTW.get(String(DISP[0].id));forceRen=true;tick(performance.now());outDraw(c,true);await sleep(300);
  const x=o&&o.x;R.outOpen=!!o;R.outPx=x?[...x.getImageData(5,5,1,1).data]:null;R.outNode=o?typeof o.win.require:'?';outClose(String(DISP[0].id))}catch(e){R.outErr=e.message}
 // print labels window (document.write into a blank child)
 try{const w2=open('','_blank');w2.document.write('<p id=x>hello</p>');w2.document.close();await sleep(300);R.blank=w2.document.getElementById('x').textContent;R.blankNode=typeof w2.require;w2.close()}catch(e){R.blankErr=e.message}
 // web pages never open in the app
 const before=location.href;const w3=open('https://example.com/','_blank');R.webWindow=w3===null?'denied':'opened';
 const a=document.createElement('a');a.href='https://example.com/';document.body.appendChild(a);a.click();await sleep(800);R.stillApp=location.href===before;
 return R})()

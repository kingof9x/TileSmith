(async()=>{const R={},fs=require('fs'),cr=require('crypto'),sleep=ms=>new Promise(r=>setTimeout(r,ms));
 process.env.APPIMAGE='/tmp/old.AppImage';const body=Buffer.from('new TileSmith build');const good='sha256:'+cr.createHash('sha256').update(body).digest('hex');
 window.addonGet=async(u,f)=>{fs.writeFileSync(f,body);return f};const sent=[];const ipc=require('electron').ipcRenderer;ipc.send=(c,j)=>sent.push([c,j&&j.cmd]);
 const mk=d=>({tag:'v99.0',assets:[{name:'TileSmith-linux-x64.AppImage',browser_download_url:'https://x/y',digest:d}]});
 await updInstall(mk('sha256:'+'0'.repeat(64)));await sleep(1000);R.bad={msg:$('#updMsg').textContent,sent:sent.length};
 UPD_BUSY=false;await updInstall(mk(good));await sleep(1200);R.good={msg:$('#updMsg').textContent,sent:sent.slice()};
 UPD_BUSY=false;sent.length=0;await updInstall(mk(undefined));await sleep(1200);R.none={sent:sent.length};
 return R})()

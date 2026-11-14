// Prints the shared lists of app/index.html (TR, S, WK, LIM) as JSON: {NAME:{start,end,kind,items:[{key,src}]}}.
// Used by tests/lists_test.py, which checks they stay one entry per line in "// Feature" groups (fewer merge conflicts).
// usage: node lists.js path/to/index.html
const acorn=require('./node_modules/acorn'),fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8'),NAMES=['TR','S','WK','LIM'],out={};
const re=/<script>([\s\S]*?)<\/script>/g;let m;
while((m=re.exec(html))){const base=m.index+8,code=m[1];const ast=acorn.parse(code,{ecmaVersion:'latest'});
 for(const st of ast.body){if(st.type!=='VariableDeclaration')continue;
  for(const d of st.declarations){const n=d.id.name,I=d.init;if(!NAMES.includes(n)||!I)continue;
   const obj=I.type==='ObjectExpression',els=obj?I.properties:I.elements;
   out[n]={start:base+I.start,end:base+I.end,kind:obj?'O':'A',items:els.map(p=>({key:obj?(p.key.type==='Identifier'?p.key.name:p.key.value):p.value,src:code.slice(p.start,p.end)}))};
 }}}
process.stdout.write(JSON.stringify(out));

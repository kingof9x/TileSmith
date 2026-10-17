// Lists the top-level statements of a JavaScript file with their line ranges (leading comments included) as JSON:
// [{names: ["render"], start: 3640, end: 3963, kind: "FunctionDeclaration"}, ...]. Used by make_route_b_prompts.py.
const fs = require('fs'), acorn = require('acorn');
const src = fs.readFileSync(process.argv[2], 'utf8'), comments = [];
const ast = acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', locations: true, onComment: comments });
const out = [];
let ci = 0, prevEnd = 0;
for (const n of ast.body) {
  let start = n.loc.start.line;
  // comments between the previous statement and this one belong to this one
  const own = comments.filter(c => c.start >= prevEnd && c.end <= n.start);
  if (own.length) start = Math.min(start, own[0].loc.start.line);
  const names = n.type === 'FunctionDeclaration' ? [n.id.name]
    : n.type === 'VariableDeclaration' ? n.declarations.flatMap(d => d.id.type === 'Identifier' ? [d.id.name] : []) : [];
  out.push({ names, start, end: n.loc.end.line, kind: n.type });
  prevEnd = n.end;
}
process.stdout.write(JSON.stringify(out));

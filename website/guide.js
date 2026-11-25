// Shared behaviour for the website's reading guides (read-the-code/, read-rust/): section navigation like the
// How TileSmith works deck, copy buttons, steppers, quizzes, the symbol decoder, the glossary filter and the file map.
// Everything works without it too: the sections are plain HTML and the first stop of every stepper is shown.
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- navigation: ←/→ jump between sections, the counter and progress bar follow the scroll ---------- */
  const deck = $('#deck'), slides = $$('.slide'), count = $('#count'), prog = $('#prog');
  let cur = 0;
  const go = (i) => { i = Math.max(0, Math.min(slides.length - 1, i)); slides[i].scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); };
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    cur = slides.indexOf(e.target);
    count.textContent = (cur + 1) + ' / ' + slides.length;
    prog.style.width = ((cur + 1) / slides.length * 100) + '%';
    try { history.replaceState(null, '', '#' + e.target.id); } catch (_) {}
  }), { root: deck, rootMargin: '-45% 0px -50% 0px', threshold: 0 });
  slides.forEach((s) => io.observe(s));
  $('#prev').onclick = () => go(cur - 1);
  $('#next').onclick = () => go(cur + 1);
  addEventListener('keydown', (e) => {
    if (/^(INPUT|SELECT|TEXTAREA|BUTTON)$/.test(document.activeElement.tagName) && !['ArrowRight', 'ArrowLeft'].includes(e.key)) return;
    if (/^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName)) return;
    if (['ArrowRight', 'PageDown'].includes(e.key)) { e.preventDefault(); go(cur + 1); }
    else if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); go(cur - 1); }
    else if (e.key === 'Home') { e.preventDefault(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); go(slides.length - 1); }
  });
  const start = slides.findIndex((s) => '#' + s.id === location.hash);
  if (start > 0) slides[start].scrollIntoView();

  /* ---------- copy buttons on .cmd blocks ---------- */
  $$('.cmd').forEach((box) => {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = 'Copy';
    b.onclick = async () => {
      const txt = $('pre', box).innerText.split('\n').filter((l) => !l.trim().startsWith('#')).join('\n').trim();
      try { await navigator.clipboard.writeText(txt); b.textContent = 'Copied'; } catch (_) { b.textContent = 'Select it'; }
      setTimeout(() => { b.textContent = 'Copy'; }, 1500);
    };
    box.appendChild(b);
  });

  /* ---------- steppers: buttons in .stops switch which .stop is shown ---------- */
  $$('.stepper').forEach((st) => {
    const btns = $$('.stops button', st), stops = $$('.stop', st);
    const show = (i) => { btns.forEach((b, k) => b.setAttribute('aria-pressed', k === i)); stops.forEach((s, k) => s.classList.toggle('on', k === i)); };
    btns.forEach((b, i) => { b.type = 'button'; b.onclick = () => show(i); });
    const nx = $('[data-next]', st);
    if (nx) nx.onclick = () => show((btns.findIndex((b) => b.getAttribute('aria-pressed') === 'true') + 1) % btns.length);
    show(0);
  });

  /* ---------- quizzes: each .q has buttons with data-a="right" or "wrong" ---------- */
  $$('.q').forEach((q) => $$('.opts button', q).forEach((b) => {
    b.type = 'button';
    b.onclick = () => {
      const ok = b.dataset.a === 'right';
      q.classList.remove('right', 'wrong'); q.classList.add('done', ok ? 'right' : 'wrong');
      $('.verdict', q).textContent = ok ? 'Right' : 'Not quite';
    };
  }));

  /* ---------- symbol decoder: pre.decode button.t[data-x] writes its explanation into the target ---------- */
  $$('pre.decode').forEach((pre) => {
    const out = $(pre.dataset.target);
    $$('button.t', pre).forEach((b) => {
      b.type = 'button';
      b.onclick = () => {
        $$('button.t', pre).forEach((x) => x.setAttribute('aria-pressed', x === b));
        // the explanation is plain text in data-x; `backticks` become code
        const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        out.innerHTML = `<b>${esc(b.dataset.h || b.textContent)}</b><p>${esc(b.dataset.x).replace(/`([^`]+)`/g, '<code>$1</code>')}</p>`;
      };
    });
  });

  /* ---------- glossary filter: input[data-filter="#table"] hides rows that don't match ---------- */
  $$('input[data-filter]').forEach((inp) => {
    const rows = $$('tbody tr', $(inp.dataset.filter));
    inp.oninput = () => { const q = inp.value.trim().toLowerCase(); rows.forEach((r) => { r.hidden = q && !r.textContent.toLowerCase().includes(q); }); };
  });

  /* ---------- the file map: a bar of coloured blocks (one per region of the file) and a clickable list ---------- */
  const fm = $('#fmdata');
  if (fm) {
    const { total, regions, colors } = JSON.parse(fm.textContent);
    const bar = $('#fmBar'), list = $('#fmList'), info = $('#fmInfo');
    const btnsB = [], btnsL = [];
    const pick = (i) => {
      const r = regions[i], end = i + 1 < regions.length ? regions[i + 1].line - 1 : total;
      btnsB.forEach((b, k) => b.setAttribute('aria-pressed', k === i));
      btnsL.forEach((b, k) => b.setAttribute('aria-pressed', k === i));
      info.innerHTML = `<b>Lines ${r.line.toLocaleString('en-US')}–${end.toLocaleString('en-US')} · ${r.title}</b><p>${r.text}</p>` +
        `<p class="mono mu">${r.grep ? 'grep -n ' + r.grep.replace(/</g, '&lt;') + ' index.html | cut -c1-150' : ''}</p>`;
      btnsL[i].scrollIntoView({ block: 'nearest' });
    };
    regions.forEach((r, i) => {
      const end = i + 1 < regions.length ? regions[i + 1].line - 1 : total;
      const b = document.createElement('button'); b.type = 'button';
      b.style.top = (r.line - 1) / total * 100 + '%'; b.style.height = Math.max(0.4, (end - r.line + 1) / total * 100) + '%';
      b.style.background = colors[r.kind]; b.setAttribute('aria-label', `${r.title}, line ${r.line}`); b.onclick = () => pick(i);
      bar.appendChild(b); btnsB.push(b);
      const l = document.createElement('button'); l.type = 'button';
      l.innerHTML = `<span>${r.line.toLocaleString('en-US')}</span>${r.title}`; l.style.borderLeft = `4px solid ${colors[r.kind]}`; l.onclick = () => pick(i);
      list.appendChild(l); btnsL.push(l);
    });
    pick(regions.findIndex((r) => r.start) || 0);
  }
})();

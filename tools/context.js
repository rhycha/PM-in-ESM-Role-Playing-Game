/* Context support is deliberately separate from the story and saved progress. */
(function () {
  'use strict';
  if (window.pm2Context || typeof SCENES === 'undefined' || typeof VTAG === 'undefined') return;
  const data = JSON.parse(document.getElementById('pm2-context-data').textContent);
  const project = data.projects[VTAG];
  const main = document.getElementById('main');
  if (!project || !main) return;
  const key = 'pm2.context.' + VTAG;
  const get = id => document.getElementById(id);
  const safe = value => String(value || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let lastScene = null, lastLine = null, expanded = false;
  try { expanded = localStorage.getItem(key) === 'open'; } catch (_) {}

  const panel = document.createElement('section');
  panel.id = 'scene-context';
  panel.setAttribute('aria-label', 'Scene context');
  panel.hidden = true;
  main.insertBefore(panel, get('stage'));

  const speaker = document.createElement('div');
  speaker.id = 'speaker-context';
  speaker.hidden = true;
  get('spk').insertAdjacentElement('afterend', speaker);
  const words = document.createElement('div');
  words.id = 'line-context';
  words.hidden = true;
  get('txt').insertAdjacentElement('afterend', words);

  // These controls must not trigger the story's click/keyboard-to-advance handler.
  [panel, words].forEach(node => {
    node.addEventListener('click', e => e.stopPropagation());
    node.addEventListener('keydown', e => e.stopPropagation());
  });

  function rolePurpose(id) {
    return (VTAG === 'pollux' && data.pollux_roles[id]) || data.roles[id] || '';
  }

  function drawScene() {
    const scene = project.scenes[cur.id];
    if (!scene) { panel.hidden = true; return; }
    const index = SCENES.findIndex(s => s.id === cur.id);
    panel.hidden = false;
    panel.innerHTML = '<div class="ctx-top"><span class="ctx-eyebrow">Scene brief · ' + safe(cur.actName) +
      ' · ' + (index + 1) + ' / ' + SCENES.length + '</span><span class="ctx-fiction">Fictional case</span></div>' +
      '<p class="ctx-situation">' + safe(scene[0]) + '</p>' +
      '<p class="ctx-focus"><b>Listen for</b> ' + safe(scene[2]) + '</p>' +
      '<details id="context-details"' + (expanded ? ' open' : '') + '><summary>Orient me: project, stakes and people</summary>' +
      '<div class="ctx-details"><div class="ctx-grid"><div><h3>' + safe(project.title) + '</h3><p>' + safe(project.goal) +
      '</p></div><div><h3>Why this scene matters</h3><p>' + safe(scene[1]) +
      '</p></div></div><p class="ctx-you"><b>Your role.</b> ' + safe(project.you) + '</p>' +
      '<h3>Who is in this scene</h3><div class="ctx-people">' + (cur.cast || []).filter(id => CAST[id]).map(id => {
        const person = CAST[id];
        return '<div><b>' + safe(person.n) + '</b><span>' + safe(person.r) + '</span><p>' + safe(rolePurpose(id)) + '</p></div>';
      }).join('') + '</div><p class="ctx-help">Follow the situation first. Learn the names and abbreviations as they appear. ' +
      'Select a word below the dialogue for a plain-language explanation; select a highlighted number for its meaning.</p>' +
      '<p class="ctx-disclaimer">' + safe(data.disclaimer) + '</p></div></details>';
    get('context-details').addEventListener('toggle', e => {
      expanded = e.target.open;
      try { localStorage.setItem(key, expanded ? 'open' : 'closed'); } catch (_) {}
    });
  }

  function contains(text, term) {
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp('(^|[^a-zA-Z])' + escaped + '(?:s|ing|d)?(?=$|[^a-zA-Z])', 'i').test(text);
  }

  function lineTerms(line) {
    const text = get('txt').textContent || line.text || '';
    const terms = [], seen = new Set();
    const add = pair => {
      if (!pair || pair.length < 2 || !contains(text, pair[0])) return;
      const id = pair[0].toLowerCase();
      if (seen.has(id)) return;
      seen.add(id); terms.push(pair);
    };
    // The author-provided definitions take precedence over the shared glossary.
    (line.g || []).forEach(add);
    data.terms.forEach(add);
    return terms;
  }

  function drawLine() {
    let line = phase === 'line' && li < cur.lines.length ? cur.lines[li] : null;
    if (phase === 'verdict' && cur.choice && S.choices[cur.id]) {
      line = cur.choice.options[S.choices[cur.id].i].reply || null;
    }
    speaker.hidden = !line;
    words.hidden = !line;
    if (!line) { speaker.textContent = ''; words.innerHTML = ''; return; }
    if (line.who === 'narr') {
      speaker.innerHTML = '<b>Narrator</b><span>Sets the scene: where you are and what you can observe.</span>';
    } else {
      const person = CAST[line.who];
      speaker.innerHTML = '<b>' + safe(person ? person.r : line.who) + '</b><span>' + safe(rolePurpose(line.who)) + '</span>';
    }
    const terms = lineTerms(line);
    words.hidden = !terms.length;
    words.innerHTML = terms.length ? '<div class="ctx-terms"><span>Words in this line</span>' + terms.map((term, index) =>
      '<button type="button" class="ctx-term" data-term="' + index + '" aria-expanded="false" aria-controls="context-definition">' + safe(term[0]) + '</button>'
    ).join('') + '</div><div id="context-definition" class="ctx-definition" hidden></div>' : '';
    words.querySelectorAll('[data-term]').forEach(button => {
      button.addEventListener('click', () => {
        const close = button.getAttribute('aria-expanded') === 'true';
        words.querySelectorAll('[data-term]').forEach(b => b.setAttribute('aria-expanded', 'false'));
        const definition = get('context-definition');
        definition.hidden = close;
        if (close) return;
        button.setAttribute('aria-expanded', 'true');
        const term = terms[Number(button.dataset.term)];
        definition.innerHTML = '<b>' + safe(term[0]) + '</b> — ' + safe(term[1]);
      });
    });
  }

  function update() {
    if (!cur) { panel.hidden = true; return; }
    if (lastScene !== cur.id) {
      lastScene = cur.id;
      drawScene();
    }
    const current = cur.id + ':' + phase + ':' + li + ':' + (get('spk').textContent || '') + ':' + get('txt').textContent;
    if (lastLine !== current) {
      lastLine = current;
      drawLine();
    }
  }

  // Observe only existing story nodes; updating this enhancement cannot trigger itself.
  const observer = new MutationObserver(update);
  ['slug', 'spk', 'txt', 'extra'].forEach(id => observer.observe(get(id), {childList: true, subtree: true, characterData: true}));
  window.pm2Context = {refresh: update, version: 1};
  update();
}());

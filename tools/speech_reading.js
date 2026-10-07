/* Shared speech text and clear-reading player. No network requests or voice downloads. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PM2Speech = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const VERSION = '2026-10-06.1';
  const ONES = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'];
  const TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'];
  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const NUM = '\\d+(?:,\\d{3})*(?:\\.\\d+)?';
  const SCALE = '(?:billion|million|thousand|bn|m|k)';
  const SAY = {
    'PM²':'P M two', 'PM2':'P M two', LOS:'L O S', EFSF:'E F S F', ESM:'E S M',
    PCCL:'P C C L', ECCL:'E C C L', PMSF:'P M S F', SMSF:'S M S F', SRF:'S R F',
    RASCI:'rasky', RfP:'R F P', RfE:'R F E', RfC:'R F C', WBS:'W B S',
    PSC:'P S C', AGB:'A G B', PCT:'P C T', PSO:'P S O', PQA:'P Q A',
    DPC:'D P C', LISO:'L I S O', DMO:'D M O', BIG:'B I G', API:'A P I', UI:'U I', IT:'I T',
    SWOT:'swot', MoSCoW:'moscow', TeCo:'Teh-co', PrOw:'Pro-Ow', ArOw:'Ar-Ow', ATeM:'A team',
    WIL:'W I L', MVP:'M V P', DoD:'D O D', CIR:'C I R', ISO:'I S O'
  };
  function cardinal(value) {
    const n = Number(String(value).replace(/,/g, ''));
    if (!Number.isSafeInteger(n)) return String(value).split('').map(d => ONES[Number(d)] || d).join(' ');
    if (n < 0) return 'minus ' + cardinal(-n);
    if (n < 20) return ONES[n];
    if (n < 100) return TENS[Math.floor(n / 10)] + (n % 10 ? '-' + ONES[n % 10] : '');
    if (n < 1000) return ONES[Math.floor(n / 100)] + ' hundred' + (n % 100 ? ' and ' + cardinal(n % 100) : '');
    for (const [scale, word] of [[1e12,'trillion'],[1e9,'billion'],[1e6,'million'],[1e3,'thousand']]) {
      if (n >= scale) return cardinal(Math.floor(n / scale)) + ' ' + word + (n % scale ? ' ' + cardinal(n % scale) : '');
    }
  }
  function decimal(value) {
    const bits = String(value).replace(/,/g, '').split('.');
    return cardinal(bits[0]) + (bits.length > 1 ? ' point ' + bits[1].split('').map(d => ONES[Number(d)]).join(' ') : '');
  }
  function ordinal(value) {
    const words = cardinal(value);
    const irregular = {one:'first',two:'second',three:'third',five:'fifth',eight:'eighth',nine:'ninth',twelve:'twelfth'};
    return words.replace(/[a-z]+$/, w => irregular[w] || (w.endsWith('y') ? w.slice(0,-1) + 'ieth' : w + 'th'));
  }
  function year(value) {
    const n = Number(value), high = Math.floor(n / 100), low = n % 100;
    if (n >= 2000 && n < 2010) return 'two thousand' + (low ? ' ' + cardinal(low) : '');
    if (n >= 1100 && n <= 2099) return cardinal(high) + (low === 0 ? ' hundred' : low < 10 ? ' oh ' + cardinal(low) : ' ' + cardinal(low));
    return cardinal(n);
  }
  function scaleWord(s) { return ({m:'million',bn:'billion',k:'thousand'})[(s || '').toLowerCase()] || (s || '').toLowerCase(); }
  function identifier(s) { return s[0] === '0' ? s.split('').map(d => ONES[Number(d)]).join(' ') : cardinal(s); }
  function normalize(text) {
    let s = String(text == null ? '' : text).replace(/[\u00a0_]/g, ' ');
    // Acronyms first: a superscript digit is not a word-boundary character.
    for (const [a, b] of Object.entries(SAY)) s = s.replace(new RegExp('(^|[^A-Za-z0-9])' + a + '(?![A-Za-z0-9])', 'g'), (_, lead) => lead + b);
    const month = '(' + MONTHS.join('|') + ')';
    s = s.replace(new RegExp('\\b(\\d{1,2})\\s+' + month + '(?:\\s+(\\d{4}))?\\b','gi'), (_, d, m, y) => 'the ' + ordinal(d) + ' of ' + m + (y ? ' ' + year(y) : ''));
    s = s.replace(new RegExp('\\b' + month + '\\s+(\\d{4})\\b','gi'), (_, m, y) => m + ' ' + year(y));
    s = s.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g, (all,y,m,d) => Number(m) >= 1 && Number(m) <= 12 && Number(d) >= 1 && Number(d) <= 31 ? 'the ' + ordinal(d) + ' of ' + MONTHS[Number(m)-1] + ' ' + year(y) : all);
    s = s.replace(/\b(\d{2})-(\d{2})-(\d{4})\b/g, (all,d,m,y) => Number(m) >= 1 && Number(m) <= 12 && Number(d) >= 1 && Number(d) <= 31 ? 'the ' + ordinal(d) + ' of ' + MONTHS[Number(m)-1] + ' ' + year(y) : all);
    s = s.replace(/\b([01]?\d|2[0-3]):([0-5]\d)(?:\s*([ap])\.?m\.?)?/gi, (_,h,m,ampm) => {
      const hour = Number(h), min = Number(m);
      return cardinal(hour % 12 || 12) + (min ? (min < 10 ? ' oh ' : ' ') + cardinal(min) : '') + ' ' + (ampm ? ampm.toUpperCase() : hour < 12 ? 'A' : 'P') + ' M';
    });
    s = s.replace(/\b([A-Z]{1,4})(\d+)-(\d+)\b/g, (_,letters,a,b) => letters.split('').join(' ') + ' ' + identifier(a) + ' ' + identifier(b));
    s = s.replace(/\b([A-Z]{1,4})-(\d+)\b/g, (_,letters,n) => letters.split('').join(' ') + ' ' + identifier(n));
    s = s.replace(/\b([A-Z]{1,4})(\d+)\b/g, (_,letters,n) => letters.split('').join(' ') + ' ' + identifier(n));
    s = s.replace(new RegExp('([€$£])\\s*(' + NUM + ')\\s*[-–—]\\s*(' + NUM + ')\\s*(' + SCALE + ')?\\b','gi'), (_,symbol,a,b,scale) => decimal(a) + ' to ' + decimal(b) + (scale ? ' ' + scaleWord(scale) : '') + ' ' + ({'€':'euros','$':'dollars','£':'pounds'})[symbol]);
    s = s.replace(new RegExp('([€$£])\\s*(' + NUM + ')\\s*(' + SCALE + ')?\\b','gi'), (_,symbol,n,scale) => decimal(n) + (scale ? ' ' + scaleWord(scale) : '') + ' ' + ({'€':'euros','$':'dollars','£':'pounds'})[symbol]);
    s = s.replace(new RegExp('\\b(' + NUM + ')\\s*[-–—]\\s*(' + NUM + ')\\s*%', 'g'), (_,a,b) => decimal(a) + ' to ' + decimal(b) + ' per cent');
    s = s.replace(new RegExp('\\b(' + NUM + ')\\s*%', 'g'), (_,n) => decimal(n) + ' per cent');
    s = s.replace(/\b(version\s+|v)(\d+(?:\.\d+)*)\b/gi, (_,label,n) => 'version ' + n.split('.').map(identifier).join(' point '));
    s = s.replace(/\b(section|chapter|work package)\s+(\d+(?:\.\d+)+)\b/gi, (_,label,n) => label + ' ' + n.split('.').map(identifier).join(' point '));
    s = s.replace(/\b\d+(?:\.\d+){2,}\b/g, n => n.split('.').map(identifier).join(' point '));
    s = s.replace(/\b(\d+)(?:st|nd|rd|th)\b/gi, (_,n) => ordinal(n));
    s = s.replace(new RegExp('\\b(' + NUM + ')\\s*[-–—]\\s*(' + NUM + ')\\b','g'), (_,a,b) => decimal(a) + ' to ' + decimal(b));
    s = s.replace(new RegExp('\\b(' + NUM + ')\\s*/\\s*(' + NUM + ')\\b','g'), (_,a,b) => decimal(a) + ' out of ' + decimal(b));
    s = s.replace(/\b(\d+):(\d+)\b/g, (_,a,b) => cardinal(a) + ' to ' + cardinal(b));
    s = s.replace(new RegExp('(^|[\\s(=])[-−](' + NUM + ')\\b','g'), (_,lead,n) => lead + 'minus ' + decimal(n));
    s = s.replace(new RegExp('\\b' + NUM + '\\b','g'), n => decimal(n));
    for (const [a,b] of Object.entries({'≥':' at least ','≤':' at most ','>':' greater than ','<':' less than ','×':' times ','÷':' divided by ','=':' equals ','+':' plus ','~':' about ','&':' and ','%':' per cent ','_':' ','/':' slash '})) s = s.split(a).join(b);
    return s.replace(/\s+/g, ' ').trim();
  }
  function sentences(text) {
    // Do this after normalization so decimals and versions cannot become stops.
    const protectedText = String(text).replace(/\b(Mr|Mrs|Ms|Dr|Prof|St|No|vs|etc|approx|e\.g|i\.e)\./gi, m => m.replace(/\./g,'\uE000'));
    const parts = protectedText.split(/(?<=[.!?])\s+(?=[“"A-Z0-9])/).map(s => s.replace(/\uE000/g,'.').trim()).filter(Boolean);
    return parts.flatMap(s => s.length > 320 ? s.split(/(?<=[;:])\s+|\s+[—–]\s+/).filter(Boolean) : [s]);
  }
  function englishVoices(synthesis) {
    const ss = synthesis || (typeof speechSynthesis !== 'undefined' ? speechSynthesis : null);
    return ss ? ss.getVoices().filter(v => /^en(?:[-_]|$)/i.test(v.lang)) : [];
  }
  function chooseVoice(preferredURI, synthesis) {
    const voices = englishVoices(synthesis);
    return voices.find(v => v.voiceURI === preferredURI || v.name === preferredURI) ||
      voices.find(v => /premium|enhanced|natural/i.test(v.name)) ||
      voices.find(v => /^(Daniel|Samantha|Alex|Karen|Moira|Tessa)(?:\b|$)/i.test(v.name)) || voices.find(v => v.default) ||
      voices.find(v => /^en-GB$/i.test(v.lang)) || voices[0] || null;
  }
  function configureUtterance(u, options) {
    const o = options || {}, voice = chooseVoice(o.preferredURI, o.synthesis);
    u.lang = voice ? voice.lang : 'en-GB';
    if (voice) u.voice = voice;
    u.pitch = 1;
    u.rate = Math.max(0.6, Math.min(1.5, Number(o.rate) || 1));
    u.volume = Math.max(0, Math.min(1, o.volume == null ? 1 : Number(o.volume)));
    return u;
  }
  function createPlayer(deps) {
    const ss = deps.synthesis, Utterance = deps.Utterance;
    const schedule = deps.setTimeout || setTimeout, unschedule = deps.clearTimeout || clearTimeout;
    let generation = 0, pending = null, watchdog = null, current = null, paused = false;
    function clearTimers() { if (pending !== null) unschedule(pending); if (watchdog !== null) unschedule(watchdog); pending = watchdog = null; }
    function cancel() {
      generation++; clearTimers(); paused = false;
      if (current) current.onend = current.onerror = null;
      current = null;
      if (ss) {
        try { ss.cancel(); } catch (_) {}
        // Web Speech cancel clears the queue but does not necessarily clear the
        // engine's paused flag. A new line must be able to start after Pause/Next.
        try { if (ss.paused) ss.resume(); } catch (_) {}
      }
    }
    function speak(text, options) {
      cancel();
      const o = options || {}, token = generation, queue = sentences(normalize(text));
      let index = 0, started = false;
      function error(err) { if (token !== generation) return; cancel(); if (o.onError) o.onError(err); }
      function next() {
        if (token !== generation) return;
        if (paused) { pending = schedule(next, 100); return; }
        if (index >= queue.length) { clearTimers(); current = null; if (o.onDone) o.onDone(); return; }
        const sentence = queue[index++];
        const u = configureUtterance(new Utterance(sentence), {...o, synthesis:ss});
        current = u;
        let ended = false;
        const valid = () => token === generation && !ended;
        u.onend = () => { if (!valid()) return; ended = true; clearTimers(); current = null; pending = schedule(next, 180); };
        u.onerror = e => { if (valid()) { ended = true; error(e); } };
        // A missing browser callback must not silently skip content or advance a scene.
        let remaining = Math.max(15000, sentence.split(/\s+/).length * 650 / u.rate + 12000);
        function check() {
          if (!valid()) return;
          if (!paused) remaining -= 500;
          if (remaining <= 0) { ended = true; error(new Error('Voice playback did not finish. Replay this line or choose another English voice.')); }
          else watchdog = schedule(check, 500);
        }
        watchdog = schedule(check, 500);
        try { ss.speak(u); if (!started && token === generation) { started = true; if (o.onStart) o.onStart(); } }
        catch (e) { error(e); }
      }
      if (!ss || !Utterance) { error(new Error('Speech synthesis is unavailable in this browser.')); return; }
      const available = ss.getVoices();
      if (available.length && !englishVoices(ss).length) { error(new Error('No English system voice is available. Choose recorded audio or install an English voice.')); return; }
      // Keep cancellation and the next utterance in separate browser ticks.
      pending = schedule(next, 60);
    }
    function pause() { paused = true; if (ss) ss.pause(); }
    function resume() { paused = false; if (ss) ss.resume(); }
    return {speak, cancel, pause, resume, isPaused: () => paused};
  }
  return {VERSION, cardinal, decimal, ordinal, year, normalize, sentences, englishVoices, chooseVoice, configureUtterance, createPlayer};
});

/* Integrate clear reading without replacing the story, recordings or saved progress. */
(function () {
  'use strict';
  if (typeof PM2Speech === 'undefined' || typeof V === 'undefined') return;
  const player = PM2Speech.createPlayer({synthesis: SS,
    Utterance: typeof SpeechSynthesisUtterance === 'undefined' ? null : SpeechSynthesisUtterance});
  let speechGeneration = 0, advanceTimer = null, pendingAdvance = null;
  function scheduleAdvance() {
    if (advanceTimer !== null) clearTimeout(advanceTimer);
    if (!pendingAdvance || vPaused) return;
    advanceTimer = setTimeout(() => { advanceTimer = null; if (pendingAdvance) pendingAdvance(); }, 300);
  }
  const oldStop = stopSpeak, oldPause = pauseVoice, oldResume = resumeVoice;
  stopSpeak = function () {
    speechGeneration++;
    if (advanceTimer !== null) clearTimeout(advanceTimer);
    advanceTimer = pendingAdvance = null;
    player.cancel(); oldStop();
  };
  pauseVoice = function () { oldPause(); if (lastVia === 'system') player.pause(); };
  resumeVoice = function () { oldResume(); if (lastVia === 'system') player.resume(); scheduleAdvance(); };

  // A one-time, visible change of the app's reading defaults, not browser settings.
  if (!V.clearReadingRevision) {
    V.clearReadingRevision = 1;
    V.src = 'system';
    V.auto = false;
    V.reader = '';
    vsave();
  }
  speakSys = function (who, text, onDone) {
    lastVia = 'system';
    player.speak(text, {
      preferredURI: V.reader || '', rate: V.rate || 1, volume: V.vol,
      onStart: function () {
        lastVia = 'system'; audioErr = '';
        if ($('spk')) $('spk').classList.add('speaking');
        const reader = PM2Speech.chooseVoice(V.reader, SS);
        if ($('readingStatus')) $('readingStatus').textContent = 'Reading with ' + (reader ? reader.name : 'the browser’s English voice') + '.';
        setBadge();
      },
      onDone: function () {
        if ($('spk')) $('spk').classList.remove('speaking');
        if ($('readingStatus')) $('readingStatus').textContent = 'Reading finished.';
        if (onDone) onDone();
      },
      onError: function (error) {
        if ($('spk')) $('spk').classList.remove('speaking');
        audioErr = error.message || error.error || 'Voice playback failed. Try another English voice.';
        toast(audioErr);
        const status = $('readingStatus');
        if (status) status.textContent = audioErr;
      }
    });
  };
  speakLine = function (who, text, onDone, id) {
    if (!V.on || !text) { if (onDone) onDone(); return; }
    stopSpeak();
    // Missing clips must not invoke the completion callback before the fallback speaks.
    if (V.src === 'recorded' && !recFail && id && VIDX[id] && playRec(id, onDone)) return;
    speakSys(who, text, onDone);
  };
  narrate = function (line) {
    if (!V.on) return;
    vPaused = false; curClip = null; curDone = null;
    const scene = cur && cur.id, lineIndex = li;
    const text = S.plain && line.plain ? line.plain : line.text;
    let run = null;
    speakLine(line.who, text, function () {
      if (run !== speechGeneration || !V.auto) return;
      pendingAdvance = function () {
        if (run !== speechGeneration || !V.on || !V.auto || vPaused || phase !== 'line' ||
            !cur || cur.id !== scene || li !== lineIndex ||
            $('ov').classList.contains('on') || $('menu').classList.contains('on')) return;
        pendingAdvance = null;
        advance();
      };
      scheduleAdvance();
    }, scene ? clipId(scene, li) : null);
    run = speechGeneration;
  };

  const sample = 'The budget is €8.4 million. There are 1,400 fields. Risk R-07 has a score of 12. The ratio is 0.08. The review is on 21st October.';
  function readSample() { stopSpeak(); speakSys('narr', sample); }
  function replayLine() {
    if (!cur || phase !== 'line' || !cur.lines[li]) return;
    stopSpeak(); V.on = true; vsave(); setBadge();
    // Replay is deliberate and never advances while the settings are open.
    const line = cur.lines[li];
    const text = S.plain && line.plain ? line.plain : line.text;
    speakLine(line.who, text, null, clipId(cur.id, li));
  }
  voicePanel = function () {
    stopSpeak();
    const voices = PM2Speech.englishVoices(SS), recorded = V.src === 'recorded';
    openOv('<div class="sheet"><h2>Voice and reading</h2>' +
      '<p class="sub">Clear reading expands numbers, dates and amounts before speaking. It uses a steady pace and the voice’s normal pitch. Pause after each line while you learn; turn on automatic advance when you are ready.</p>' +
      '<div class="vopts"><label><input id="vOn" type="checkbox"' + (V.on ? ' checked' : '') + '> Voice on</label>' +
      '<label><input id="vAuto" type="checkbox"' + (V.auto ? ' checked' : '') + '> Advance automatically</label></div>' +
      '<div class="srcpick"><button id="srcSys" class="srcbtn' + (!recorded ? ' on' : '') + '"><b>Clear reading</b><span>Corrected number text and one English reader.</span></button>' +
      '<button id="srcRec" class="srcbtn' + (recorded ? ' on' : '') + '"><b>Existing recordings</b><span>The original character voices. Earlier pronunciation errors remain in these files.</span></button></div>' +
      '<label style="display:block;margin:18px 0 8px">English reader <select id="clearReader" style="max-width:100%;display:block;margin-top:6px;padding:8px;background:#111927;color:#eef2f8;border:1px solid #516078;border-radius:6px">' +
      '<option value="">Automatic English voice</option>' + voices.map(function (voice) {
        const id = voice.voiceURI || voice.name;
        return '<option value="' + esc(id) + '"' + (V.reader === id ? ' selected' : '') + '>' + esc(voice.name + ' · ' + voice.lang) + '</option>';
      }).join('') + '</select></label>' +
      '<p class="sub">Voice quality and availability depend on this browser and device. Some browser voices use an online service. Existing recordings play from the voice folder beside the page.</p>' +
      '<div class="vopts"><label>Speed <input id="vRate" type="range" min="0.6" max="1.5" step="0.05" value="' + (V.rate || 1) + '"> <b id="vRateN">' + (V.rate || 1).toFixed(2) + '×</b></label>' +
      '<label>Volume <input id="vVol" type="range" min="0" max="1" step="0.05" value="' + (V.vol == null ? 1 : V.vol) + '"></label></div>' +
      '<div class="diag"><b>Check the numbers</b><p>' + esc(sample) + '</p>' +
      '<button class="vtest" id="testNumbers">Listen to number sample</button> <button class="vtest" id="stopReading">Stop</button>' +
      '<details style="margin-top:12px"><summary>Words sent to the reader</summary><p>' + esc(PM2Speech.normalize(sample)) + '</p></details></div>' +
      '<p id="readingStatus" role="status" class="sub">' + esc(audioErr || (recorded ? 'Selected: existing recordings.' : 'Selected: clear reading.')) + '</p>' +
      '<button class="vtest" id="replayReading"' + (cur && phase === 'line' ? '' : ' disabled') + '>Replay current line</button>' +
      '</div>');
    $('vOn').onchange = e => { V.on = e.target.checked; vsave(); setBadge(); if (!V.on) stopSpeak(); };
    $('vAuto').onchange = e => { V.auto = e.target.checked; vsave(); };
    $('srcSys').onclick = () => { stopSpeak(); V.src = 'system'; vsave(); setBadge(); voicePanel(); };
    $('srcRec').onclick = () => { stopSpeak(); V.src = 'recorded'; recFail = false; audioErr = ''; vsave(); setBadge(); voicePanel(); };
    $('clearReader').onchange = e => { stopSpeak(); V.reader = e.target.value; V.src = 'system'; vsave(); voicePanel(); };
    $('vRate').oninput = e => { V.rate = +e.target.value; $('vRateN').textContent = V.rate.toFixed(2) + '×'; vsave(); if (AU) AU.playbackRate = V.rate; };
    $('vVol').oninput = e => { V.vol = +e.target.value; vsave(); if (AU) AU.volume = V.vol; };
    $('testNumbers').onclick = readSample;
    $('stopReading').onclick = () => { stopSpeak(); $('readingStatus').textContent = 'Reading stopped.'; };
    $('replayReading').onclick = replayLine;
  };
  // The original button closures resolve the updated voicePanel at click time.
  const oldBadge = setBadge;
  setBadge = function () {
    oldBadge();
    const button = $('bVoiceTgl');
    if (!button) return;
    if (!V.on) { button.textContent = 'Voice off'; button.title = 'Turn on ' + (V.src === 'recorded' ? 'existing recordings' : 'clear reading'); }
    else if (lastVia === 'system') { button.textContent = vPaused ? 'Reading paused' : 'Clear reading'; button.title = 'English reading with expanded numbers. Voice settings are in More.'; }
  };
  // Stop any sample when the overlay is closed; this does not alter saved progress.
  $('ovx').addEventListener('click', stopSpeak);
  $('ov').addEventListener('click', e => {
    if (e.target === $('ov') || e.target === $('ovBody') || e.target.closest('.closerow')) stopSpeak();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') stopSpeak(); });
  setBadge();
})();

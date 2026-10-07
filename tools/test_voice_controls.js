/* Integration contracts: missing recordings, cancel, pause, and saved progress. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    const classes = new Set();
    elements.set(id, {textContent: '', classList: {
      add(name){classes.add(name);}, remove(name){classes.delete(name);}, contains(name){return classes.has(name);}
    }, addEventListener(){}});
  }
  return elements.get(id);
}
let now = 0, timerId = 0;
const timers = new Map();
function later(callback, delay) { const id = ++timerId; timers.set(id, {at: now + delay, callback}); return id; }
function tick(milliseconds) {
  const until = now + milliseconds;
  for (;;) {
    const next = [...timers.entries()].filter(([, timer]) => timer.at <= until).sort((a,b) => a[1].at - b[1].at)[0];
    if (!next) break;
    const [id, timer] = next; timers.delete(id); now = timer.at; timer.callback();
  }
  now = until;
}
const calls = {cancel: 0, speak: [], recorded: 0, advanced: 0};
const player = {cancel(){calls.cancel++;}, pause(){calls.paused = true;}, resume(){calls.paused = false;},
  speak(text, options){calls.speak.push({text, options});}};
const context = {PM2Speech: {createPlayer(){return player;}, chooseVoice(){return {name:'English test'};},
    englishVoices(){return [];}, normalize(text){return text;}},
  V: {on:true,src:'recorded',auto:true,rate:1,vol:1,cast:{}}, SS:{}, SpeechSynthesisUtterance:function(){},
  VIDX:{exists:['recording',0,1]}, S:{seen:{s01:true}, choices:{s02:{i:2}}},
  stopSpeak(){}, pauseVoice(){context.vPaused=true;}, resumeVoice(){context.vPaused=false;},
  speakSys(){}, speakLine(){}, narrate(){}, voicePanel(){}, setBadge(){}, vsave(){}, $:element,
  setTimeout:later, clearTimeout(id){timers.delete(id);}, clipId(){return null;},
  advance(){calls.advanced++; context.stopSpeak(); context.li++;},
  openOv(){element('ov').classList.add('on');}, esc(text){return String(text);}, AU:null,
  document:{addEventListener(){}}, lastVia:'system',audioErr:'',recFail:false,vPaused:false,
  playRec(){calls.recorded++;return true;},toast(){},cur:null,phase:'line',li:0,curClip:null,curDone:null};
const progress = JSON.stringify(context.S);
vm.createContext(context);
vm.runInContext(fs.readFileSync(__dirname+'/voice_controls.js','utf8'),context);
assert.equal(context.V.src,'system');
assert.equal(context.V.auto,false);
assert.equal(JSON.stringify(context.S),progress);
context.V.src='recorded';
let completed=0;
context.speakLine('narr','0.08',()=>completed++,'missing');
assert.equal(calls.recorded,0);
assert.equal(completed,0,'missing recording must not advance before fallback');
assert.equal(calls.speak[0].text,'0.08');
calls.speak[0].options.onDone();
assert.equal(completed,1);
context.speakLine('narr','A line',()=>completed++,'exists');
assert.equal(calls.recorded,1);
context.pauseVoice(); assert.equal(calls.paused,true);
context.resumeVoice(); assert.equal(calls.paused,false);
const prior=calls.cancel; context.stopSpeak(); assert.equal(calls.cancel,prior+1);

// The last utterance can finish just before the learner pauses or opens settings.
// Exercise that interval independently of the speech engine's own cancellation.
context.V.src='system'; context.V.auto=true;
const line={who:'narr',text:'The budget is eight point four million euros.'};
context.cur={id:'s01',lines:[line]};
function finishNarration() {
  context.li=0; context.narrate(line);
  const done=calls.speak.at(-1).options.onDone;
  done(); return done;
}
finishNarration();
context.pauseVoice(); tick(300);
assert.equal(calls.advanced,0,'pause during the completion delay must hold the line');
context.resumeVoice(); tick(299);
assert.equal(calls.advanced,0,'resume must retain the completion delay');
tick(1);
assert.equal(calls.advanced,1,'resume must advance the completed line once');
context.resumeVoice(); tick(300);
assert.equal(calls.advanced,1,'a repeated resume must not advance twice');

const staleDone=finishNarration();
context.stopSpeak(); tick(300);
assert.equal(calls.advanced,1,'stop during the completion delay must cancel advance');
staleDone(); tick(300);
assert.equal(calls.advanced,1,'a stale completion callback must not restore cancelled advance');

finishNarration();
context.voicePanel(); tick(300);
assert.equal(calls.advanced,1,'opening voice settings during the delay must preserve the line');
element('ov').classList.remove('on');
context.resumeVoice(); tick(300);
assert.equal(calls.advanced,1,'closing settings must not resurrect the cancelled advance');

context.narrate(line);
element('menu').classList.add('on');
calls.speak.at(-1).options.onDone(); tick(300);
assert.equal(calls.advanced,1,'an open menu must prevent automatic advance');
context.stopSpeak(); element('menu').classList.remove('on');
assert.equal(JSON.stringify(context.S),progress,'playback controls must not rewrite learning progress');
context.V.src='recorded';
vm.runInContext(fs.readFileSync(__dirname+'/voice_controls.js','utf8'),context);
assert.equal(context.V.src,'recorded','saved source choice must survive subsequent visits');
assert.equal(JSON.stringify(context.S),progress);
console.log('Voice integration: fallback, completion-delay cancellation, pause/resume, settings, preferences and progress passed.');

'use strict';
const assert = require('node:assert/strict');
const speech = require('../tools/speech_reading.js');
const cases = require('./speech_cases.json');
for (const [input, expected] of cases) assert.equal(speech.normalize(input), expected, input);

const french = {name:'Thomas',voiceURI:'fr',lang:'fr-FR',default:true};
const novelty = {name:'Boing',voiceURI:'boing',lang:'en-US',default:true};
const daniel = {name:'Daniel',voiceURI:'daniel',lang:'en-GB'};
const premium = {name:'Samantha (Enhanced)',voiceURI:'sam',lang:'en-US'};
let spoken, clock, tasks, ids, cancels, ss;
function setup(voices = [french,novelty,daniel]) {
  spoken=[]; clock=0; tasks=new Map(); ids=0; cancels=0;
  ss={paused:false,getVoices:()=>voices,speak:u=>spoken.push(u),cancel:()=>cancels++,pause(){this.paused=true;},resume(){this.paused=false;}};
  return speech.createPlayer({synthesis:ss,Utterance:function(text){this.text=text;},
    setTimeout:(fn,delay)=>{const id=++ids;tasks.set(id,{fn,at:clock+delay});return id;},
    clearTimeout:id=>tasks.delete(id)});
}
function tick(ms) {
  const target=clock+ms;
  while(true) {
    const next=[...tasks].sort((a,b)=>a[1].at-b[1].at)[0];
    if(!next || next[1].at>target) break;
    clock=next[1].at;tasks.delete(next[0]);next[1].fn();
  }
  clock=target;
}
setup();
assert.deepEqual(speech.englishVoices(ss),[novelty,daniel]);
assert.equal(speech.chooseVoice('',ss),daniel);
assert.equal(speech.chooseVoice('fr',ss),daniel);
assert.equal(speech.chooseVoice('boing',ss),novelty); // explicit choice is honored
setup([daniel,premium]);
assert.equal(speech.chooseVoice('',ss),premium);
let player=setup(), done=0, errors=0, starts=0;
player.speak('The cost is €8.4m. It changes by 0.08%.', {rate:0.85,volume:0.6,onDone:()=>done++,onError:()=>errors++,onStart:()=>starts++});
tick(60);
assert.equal(spoken.length,1);
assert.equal(spoken[0].text,'The cost is eight point four million euros.');
assert.equal(spoken[0].lang,'en-GB');
assert.equal(spoken[0].voice,daniel);
assert.equal(spoken[0].pitch,1);
assert.equal(spoken[0].rate,0.85);
assert.equal(spoken[0].volume,0.6);
spoken[0].onend();tick(180);
assert.equal(spoken[1].text,'It changes by zero point zero eight per cent.');
spoken[1].onend();tick(180);
assert.equal(done,1);assert.equal(starts,1);assert.equal(errors,0);assert.equal(tasks.size,0);

// Stop before delayed start must never resurrect a canceled line.
player=setup();done=0;
player.speak('Old line.',{onDone:()=>done++});player.cancel();tick(120000);
assert.equal(spoken.length,0);assert.equal(done,0);assert.equal(tasks.size,0);
// Even a browser callback already queued before cancel is stale.
player.speak('First.',{onDone:()=>done++});tick(60);
const stale=spoken[0].onend;
player.speak('Replacement.',{onDone:()=>done++});stale();tick(60);
assert.equal(spoken.length,2);assert.equal(spoken[1].text,'Replacement.');assert.equal(done,0);
spoken[1].onend();tick(180);assert.equal(done,1);

// Browser cancel may keep its global paused flag; Pause followed by Next must
// resume the engine before enqueuing the replacement.
player=setup();done=0;
player.speak('Paused line.',{onDone:()=>done++});tick(60);player.pause();
assert.equal(ss.paused,true);
player.speak('Next line.',{onDone:()=>done++});tick(60);
assert.equal(ss.paused,false);assert.equal(player.isPaused(),false);
assert.equal(spoken[1].text,'Next line.');spoken[1].onend();tick(180);assert.equal(done,1);

// Watchdogs respect pauses and report failure instead of auto-advancing.
player=setup();done=0;errors=0;
player.speak('One line.',{onDone:()=>done++,onError:()=>errors++});tick(60);
player.pause();tick(120000);assert.equal(errors,0);assert.equal(player.isPaused(),true);
player.resume();tick(16000);assert.equal(errors,1);assert.equal(done,0);assert.equal(tasks.size,0);
player=setup([french]);errors=0;
player.speak('English.',{onError:()=>errors++});tick(100);
assert.equal(errors,1);assert.equal(spoken.length,0);
player=setup();done=0;errors=0;
player.speak('First sentence. Never read this.',{onDone:()=>done++,onError:()=>errors++});tick(60);
spoken[0].onerror({error:'synthesis-failed'});tick(120000);
assert.equal(errors,1);assert.equal(done,0);assert.equal(spoken.length,1);
assert.deepEqual(speech.sentences(speech.normalize('Dr. Curie checks 1.05 million. It is correct.')),['Dr. Curie checks one point zero five million.','It is correct.']);
console.log(`PASS: ${cases.length} pronunciation fixtures; voice selection; sentence queue; cancellation; pause; errors; watchdog.`);

"""Run with python3 -m unittest discover -s tests -p 'test_*.py'."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from vnorm import norm
from make_voices import PAGES, cache_key, jobs_for, json_constant, page_with_index


class SpeechNormalizationTests(unittest.TestCase):
    def test_pronunciation_regressions(self):
        for source, expected in json.loads((ROOT / 'tests/speech_cases.json').read_text()):
            with self.subTest(source=source):
                self.assertEqual(norm(source), expected)

    def test_audio_cache_invalidates_when_speech_inputs_change(self):
        initial = cache_key('0.08 million', [0, 1.0], 'model', 'normalizer')
        self.assertNotEqual(initial, cache_key('0.8 million', [0, 1.0], 'model', 'normalizer'))
        self.assertNotEqual(initial, cache_key('0.08 million', [0, 1.0], 'model', 'new normalizer'))
        self.assertNotEqual(initial, cache_key('0.08 million', [0, 1.0], 'new model', 'normalizer'))

    def test_selective_regeneration_stays_within_selected_act(self):
        jobs = jobs_for('castor', 'plain', 1)
        self.assertEqual(list(jobs), ['castor_act1_p'])
        self.assertEqual(len(jobs['castor_act1_p']), 165)
        self.assertTrue(all(cid.startswith('castor:') and cid.endswith(':p') for cid, _, _ in jobs['castor_act1_p']))

    def test_render_plan_matches_every_active_line_and_choice_reply(self):
        for tag, name in PAGES.items():
            text = (ROOT / 'play' / name).read_text()
            payload, _, _ = json_constant(text, 'P')
            expected = {}
            for scene in payload['S']:
                for i, line in enumerate(scene['lines']):
                    expected[f"{tag}:{scene['id']}:{i}:p"] = (line['who'], line['text'])
                for i, option in enumerate((scene.get('choice') or {}).get('options', [])):
                    if option.get('reply'):
                        reply = option['reply']
                        expected[f"{tag}:{scene['id']}:c{i}:p"] = (reply['who'], reply['text'])
            planned = {cid:(who,spoken) for rows in jobs_for(tag).values() for cid,who,spoken in rows}
            self.assertEqual(planned, expected)
            current_index, _, _ = json_constant(text, 'VIDX')
            self.assertEqual(set(planned), set(current_index))
        # This specifically distinguishes the active script from archived JSON.
        first = jobs_for('castor', act=1)['castor_act1_p'][0][2]
        self.assertIn('Grace Hopper is standing at a desk', first)
        with self.assertRaises(ValueError):
            jobs_for('castor', take='natural')

    def test_timing_sync_preserves_everything_outside_selected_act(self):
        text = (ROOT / 'play' / PAGES['castor']).read_text()
        key = 'castor_act1_p'
        rows = jobs_for('castor', act=1)[key]
        entries = {cid:[key+'_testhash',i*2.0,1.8] for i,(cid,_,_) in enumerate(rows)}
        revised = page_with_index(text, key, rows, entries)
        before, start, end = json_constant(text, 'VIDX')
        after, new_start, new_end = json_constant(revised, 'VIDX')
        self.assertEqual(text[:start], revised[:new_start])
        self.assertEqual(text[end:], revised[new_end:])
        self.assertEqual({cid:entry for cid,entry in after.items() if cid not in entries},
                         {cid:entry for cid,entry in before.items() if cid not in entries})
        self.assertEqual({cid:after[cid] for cid in entries},entries)

    def test_stale_audio_and_incomplete_timing_tables_are_refused(self):
        text = (ROOT / 'play' / PAGES['castor']).read_text()
        key = 'castor_act1_p'
        rows = jobs_for('castor', act=1)[key]
        entries = {cid:[key,i*2.0,1.8] for i,(cid,_,_) in enumerate(rows)}
        stale = list(rows)
        stale[0] = (stale[0][0],stale[0][1],'The archived script is different.')
        with self.assertRaisesRegex(ValueError,'Dialogue changed'):
            page_with_index(text,key,stale,entries)
        entries.pop(rows[0][0])
        with self.assertRaisesRegex(ValueError,'playback slots'):
            page_with_index(text,key,rows,entries)

    @unittest.skipUnless(shutil.which('node'), 'Node is required for browser/Python parity')
    def test_entire_corpus_matches_browser_normalizer(self):
        lines = []
        for path in sorted((ROOT / 'tools').glob('lines_*.json')):
            for row in json.loads(path.read_text()):
                for take in ('plain', 'natural'):
                    lines.append(row[take])
        for rows in jobs_for().values():
            lines.extend(text for _,_,text in rows)
        self.assertGreater(len(lines), 5500)
        code = "const s=require('./tools/speech_reading.js');let t='';process.stdin.on('data',x=>t+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(t).map(s.normalize))));"
        result = subprocess.run(['node', '-e', code], input=json.dumps(lines), text=True, capture_output=True, cwd=ROOT, check=True)
        for text, browser in zip(lines, json.loads(result.stdout)):
            with self.subTest(source=text):
                self.assertEqual(norm(text), browser)
                self.assertNotRegex(browser, r'\d')


if __name__ == '__main__':
    unittest.main()

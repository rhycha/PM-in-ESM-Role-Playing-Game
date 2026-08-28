# -*- coding: utf-8 -*-
import json, sys, os, re

CSS=open('gen/game_css.txt').read()
BODY=open('gen/body3.html').read()
JS=open('gen/game_js.txt').read()
AV=open('gen/avatar.js').read()

def build(which):
    if which=='castor':
        title="Project CASTOR — PM² end to end"
        payload=json.load(open('src/game_payload.json'))
        vidx=json.load(open('src/vidx2_castor.json' if os.path.exists('src/vidx2_castor.json') else 'src/vidx_castor.json'))
        out='out/06_Project_CASTOR_EN.html'
        js=JS
        js=js.replace("__VTAGLINE__","")
        proj='CASTOR'; vtag='castor'; key='pm2castor.v1'
    else:
        title="Project POLLUX — PM²-Agile end to end"
        payload=json.load(open('src/pollux_payload.json'))
        vidx=json.load(open('src/vidx2_pollux.json' if os.path.exists('src/vidx2_pollux.json') else 'src/vidx_pollux.json'))
        out='out/09_Project_POLLUX_EN.html'
        js=JS
        proj='POLLUX'; vtag='pollux'; key='pm2pollux.v1'
        R=[
 ("const KEY='pm2castor.v1';","const KEY='pm2pollux.v1';"),
 ("'<p class=\"tag\">The PM&sup2; methodology, end to end, as one project at the European Stability Mechanism. '+\n   'You are the Project Manager. 52 scenes, '+SCENES.reduce((a,s)=>a+s.lines.length,0)+' lines, 31 decisions, every artefact and all thirteen Monitor &amp; Control processes.</p>'+",
  "'<p class=\"tag\">PM&sup2;-Agile, end to end, as the sequel to Project CASTOR — same institution, same people, built on the platform CASTOR delivered. '+\n   'You are the Project Manager. 25 scenes, '+SCENES.reduce((a,s)=>a+s.lines.length,0)+' lines, 14 decisions, all five ceremonies, the four core roles and every agile artefact.</p>'+"),
 ("S.unlocked.length+' of 33 artefacts unlocked &middot; progress saves in this browser.</p></div>';",
  "S.unlocked.length+' of 42 atlas entries unlocked &middot; progress saves in this browser.</p></div>';"),
 ("'<button class=\"refchip\" id=\"rc\">PM&sup2; Guide p.'","'<button class=\"refchip\" id=\"rc\">PM&sup2;-Agile Guide p.'"),
 ("<u>Guide check &middot; PM² Guide v3.1 p.","<u>Guide check &middot; PM²-Agile Guide v3.0.1 p."),
 ("<h2>Cast</h2><p class=\"sub\">One famous person per PM&sup2; role,","<h2>Cast</h2><p class=\"sub\">One famous person per PM²-Agile role,"),
 ("Full structure diagram and every field: see the Artefact Atlas.","Full diagram and every part: see the PM²-Agile Atlas."),
 ("<h2>Coverage</h2><p class=\"sub\">Every activity and artefact the PM&sup2; Guide prescribes, and the scene where you met it. ",
  "<h2>Coverage</h2><p class=\"sub\">Every entry in the PM²-Agile Atlas, and the scene where you met it. "),
 ("'<div class=\"sheet\"><h2>Artefacts</h2><p class=\"sub\">'+S.unlocked.length+' of 33 unlocked, each filled with real Project CASTOR content.</p>'",
  "'<div class=\"sheet\"><h2>Atlas</h2><p class=\"sub\">'+S.unlocked.length+' of 42 unlocked, each filled with real Project POLLUX content.</p>'"),
 ("<h1>Project <em>CASTOR</em></h1>","<h1>Project <em>POLLUX</em></h1>"),
 ("<b>The project is fictional.</b> The ESM is real; Project CASTOR, its people and its figures are invented for teaching.",
  "<b>The project is fictional.</b> The ESM is real; Projects CASTOR and POLLUX, their people and their figures are invented for teaching."),
        ]
        for a,b in R:
            if a not in js: print("  !! replacement missed:", a[:70]); continue
            js=js.replace(a,b)
    body=BODY
    if which!='castor':
        body=body.replace('Project CASTOR<span>PM&sup2; end to end</span>','Project POLLUX<span>PM&sup2;-Agile end to end</span>')
        body=body.replace('id="bArt">Artefacts','id="bArt">Atlas')
    js=js.replace('__AVATAR__',AV)
    js=js.replace('const P=__PAYLOAD__;','const PROJ='+json.dumps(proj)+';\nconst P='+json.dumps(payload,ensure_ascii=False)+';')
    head=("const VTAG="+json.dumps(vtag)+";\nconst VIDX="+json.dumps(vidx.get('clips',vidx),ensure_ascii=False)+";\n"
          "const VACT="+json.dumps(vidx.get('acts',{}),ensure_ascii=False)+";\n")
    html=("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
          "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
          "<title>"+title+"</title>\n<style>"+CSS+"</style>\n</head>\n<body>\n"+body+
          "\n<script>\n"+head+js+"\n</script>\n</body>\n</html>\n")
    open(out,'w').write(html)
    print(which,'->',out, '%.2f MB'%(os.path.getsize(out)/1e6))

for w in (sys.argv[1:] or ['castor','pollux']): build(w)

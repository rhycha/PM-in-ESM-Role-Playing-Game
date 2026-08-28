function avatar(id,size){
  const c=CAST[id]; if(!c) return '';
  const s=size||120, ac=c.accent||'#999', sk=c.skin, hr=c.hair;
  const P=[];
  P.push('<ellipse cx="50" cy="108" rx="32" ry="5" fill="#000" opacity=".25"/>');
  const cl=c.cloth||'#333', col=c.collar||'round';
  P.push('<path d="M13,112 C13,88 28,79 50,79 C72,79 87,88 87,112 Z" fill="'+cl+'"/>');
  P.push('<path d="M43,71 h14 v13 l-7,7 -7,-7 Z" fill="'+sk+'"/>');
  P.push('<path d="M43,71 h14 v6 q-7,5 -14,0 Z" fill="#000" opacity=".12"/>');
  if(col==='wing'){
    P.push('<path d="M39,79 L50,94 L61,79 L56,76 L50,88 L44,76 Z" fill="#f6f4ee"/>');
    P.push('<path d="M44,80 L50,90 L56,80 L53,78 L50,84 L47,78 Z" fill="'+ac+'"/>');
    P.push('<path d="M50,89 L46,112 L54,112 Z" fill="'+ac+'"/>');
  } else if(col==='high'){
    P.push('<path d="M35,79 C35,93 65,93 65,79 L65,89 C65,100 35,100 35,89 Z" fill="#f4f1e8"/>');
    P.push('<circle cx="50" cy="90" r="3" fill="'+ac+'"/>');
  } else if(col==='lace'){
    P.push('<path d="M28,84 C28,73 72,73 72,84 C72,95 61,100 50,100 C39,100 28,95 28,84 Z" fill="#faf7ef"/>');
    P.push('<g fill="#e2dbc8"><circle cx="34" cy="88" r="2.8"/><circle cx="42" cy="93" r="2.8"/><circle cx="50" cy="95" r="2.8"/><circle cx="58" cy="93" r="2.8"/><circle cx="66" cy="88" r="2.8"/></g>');
  } else if(col==='uniform'){
    P.push('<path d="M39,79 L50,96 L61,79 L56,76 L50,89 L44,76 Z" fill="#f6f4ee"/>');
    P.push('<path d="M50,93 L47,112 L53,112 Z" fill="#0d1523"/>');
    P.push('<g fill="'+ac+'"><rect x="16" y="93" width="15" height="3.6" rx="1.8"/><rect x="16" y="99" width="15" height="3.6" rx="1.8"/><rect x="69" y="93" width="15" height="3.6" rx="1.8"/><rect x="69" y="99" width="15" height="3.6" rx="1.8"/></g>');
  } else if(col==='bowtie'){
    P.push('<path d="M40,79 L50,91 L60,79 L56,76 L50,85 L44,76 Z" fill="#f6f4ee"/>');
    P.push('<path d="M50,88 L37,82 L37,95 Z M50,88 L63,82 L63,95 Z" fill="'+ac+'"/><circle cx="50" cy="88.5" r="3.2" fill="'+ac+'"/>');
  } else if(col==='tweed'){
    P.push('<path d="M40,79 L50,94 L60,79 L56,76 L50,88 L44,76 Z" fill="#efeade"/>');
    P.push('<path d="M38,79 L27,112 L45,112 L50,94 Z M62,79 L73,112 L55,112 L50,94 Z" fill="'+cl+'"/>');
    P.push('<path d="M50,93 L46,112 L54,112 Z" fill="'+ac+'"/>');
  } else {
    P.push('<path d="M41,78 L50,95 L59,78 L55,75 L50,89 L45,75 Z" fill="#f2eee2" opacity=".92"/>');
  }
  // head
  P.push('<ellipse cx="26" cy="50" rx="4.6" ry="6.6" fill="'+sk+'"/><ellipse cx="74" cy="50" rx="4.6" ry="6.6" fill="'+sk+'"/>');
  P.push('<ellipse cx="50" cy="48" rx="23.5" ry="27" fill="'+sk+'"/>');
  // eyes / brows / nose
  P.push('<ellipse cx="41" cy="47" rx="2.7" ry="3.1" fill="#20242c"/><ellipse cx="59" cy="47" rx="2.7" ry="3.1" fill="#20242c"/>');
  P.push('<circle cx="42" cy="45.8" r=".9" fill="#fff" opacity=".85"/><circle cx="60" cy="45.8" r=".9" fill="#fff" opacity=".85"/>');
  const bw=(c.moustache==='bushy'||c.moustache==='walrus')?3.4:2.4;
  P.push('<path d="M34,39.5 q7,-4.6 13,-1.2" stroke="'+hr+'" stroke-width="'+bw+'" fill="none" stroke-linecap="round"/>');
  P.push('<path d="M66,39.5 q-7,-4.6 -13,-1.2" stroke="'+hr+'" stroke-width="'+bw+'" fill="none" stroke-linecap="round"/>');
  P.push('<path d="M50,50 q-2.6,7 1.6,8.6" stroke="#000" stroke-opacity=".16" stroke-width="1.7" fill="none" stroke-linecap="round"/>');
  // beard, then a skin patch so the mouth stays visible
  if(c.beardPath){
    P.push('<path d="'+c.beardPath+'" fill="'+hr+'"/>');
    P.push('<ellipse cx="50" cy="63.5" rx="8.5" ry="5.6" fill="'+sk+'"/>');
  }
  P.push('<path d="M44,64 q6,4 12,0" stroke="#8a5348" stroke-width="2.1" fill="none" stroke-linecap="round"/>');
  if(c.moustache==='walrus') P.push('<path d="M32,59 C38,54 46,56.5 50,60 C54,56.5 62,54 68,59 C64,69 55,66 50,63 C45,66 36,69 32,59 Z" fill="'+hr+'"/>');
  if(c.moustache==='bushy')  P.push('<path d="M31,57 C38,52 46,55.5 50,59 C54,55.5 62,52 69,57 C67,71 56,68 50,64 C44,68 33,71 31,57 Z" fill="'+hr+'"/>');
  if(c.moustache==='thin')   P.push('<path d="M40,58.5 C44,56.5 47,57.5 50,59.5 C53,57.5 56,56.5 60,58.5 C56,62 53,60.8 50,61.8 C47,60.8 44,62 40,58.5 Z" fill="'+hr+'"/>');
  if(c.bunPath) P.push('<path d="'+c.bunPath+'" fill="'+hr+'"/>');
  if(c.hairPath) P.push('<path d="'+c.hairPath+'" fill="'+hr+'"/>');
  if(c.partLine) P.push('<path d="M50,22 L50,33" stroke="'+sk+'" stroke-width="1.6" opacity=".55" stroke-linecap="round"/>');
  if(c.hatPath) P.push('<path d="'+c.hatPath+'" fill="'+(c.hatFill||hr)+'"/>');
  if(c.glasses==='round'){
    P.push('<g fill="none" stroke="#2b313a" stroke-width="2.1"><circle cx="41" cy="47" r="9.2"/><circle cx="59" cy="47" r="9.2"/>'
      +'<path d="M50.2,47 h-0.4"/><path d="M31.8,45 l-6.5,2.4"/><path d="M68.2,45 l6.5,2.4"/></g>'
      +'<line x1="49.8" y1="46.6" x2="50.2" y2="46.6" stroke="#2b313a" stroke-width="2.1"/>');
  }
  return '<svg viewBox="0 0 100 112" width="'+s+'" height="'+Math.round(s*1.12)+'" aria-hidden="true">'+P.join('')+'</svg>';
}

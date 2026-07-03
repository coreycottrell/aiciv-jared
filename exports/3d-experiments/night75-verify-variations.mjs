import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, 'night75-renders'); fs.mkdirSync(outDir, { recursive: true });
const file = 'gleb-night75-avatar-tight-cyan-rim-antiwhiten.html';

// SAME context-safe classifier as N67-N74 (numbers stay comparable N1->N75).
// Returns ONLY numbers, never an image into context (image-context-safety).
// N75 asks: does INVERTING the spreads (cyan TIGHT rim, swept POWER 3.5/4.0/4.5 so it
// VACATES the center; warm BROAD to refill orange center) under HARDER anti-whiten
// (exposure 0.82 + bloom threshold 1.05) reach cyanMass>=8 with whiteClip<3 WHILE the
// vacated center lets orangeCenterDensity recover >=3 -- the first true three-floor pass?
// If tight-rim cyan CANNOT reach 8% without whiteClip>3, that is the decisive result
// that the covenant is geometrically over-constrained at this framing (N74 open-loop #1).
const ANALYZE = () => {
  const c = document.querySelector('canvas'); if (!c) return { error: 'no-canvas' };
  const S = 256; const off = document.createElement('canvas'); off.width = off.height = S;
  const ctx = off.getContext('2d'); try { ctx.drawImage(c, 0, 0, S, S); } catch (e) { return { error: 'draw:' + e.message }; }
  const d = ctx.getImageData(0, 0, S, S).data;
  let n=0,voidPx=0,cyan=0,orangeAll=0,nonBlank=0,lumSum=0,maxLum=0;
  let orangeCenter=0, orangeLR=0, cyanCenter=0;
  let centerN=0, lrN=0;
  let frBloom=0, frN=0, frWarm=0;
  let whiteClip=0; // N74 diag: near-white bright pixels (cyan that clipped past the test)
  for (let i=0;i<d.length;i+=4){
    const px=(i/4)%S, py=Math.floor((i/4)/S);
    const r=d[i],g=d[i+1],b=d[i+2]; const lum=0.2126*r+0.7152*g+0.0722*b;
    lumSum+=lum; if(lum>maxLum)maxLum=lum;
    if(r<24&&g<28&&b<34)voidPx++; if(lum>12)nonBlank++;
    const isCyan = (b>70&&b>=g&&g>r+15&&lum>40);
    if(isCyan)cyan++;
    if(r>200&&g>200&&b>200)whiteClip++;
    const isOrange = (r>120&&r>g+40&&g>b&&b<90);
    const inCenter = (px>S*0.32 && px<S*0.68 && py>S*0.30 && py<S*0.70);
    const inLR     = (px>S*0.55 && py>S*0.55);
    if(inCenter){ centerN++; if(isCyan)cyanCenter++; }
    if(inLR) lrN++;
    if(isOrange){ orangeAll++; if(inCenter)orangeCenter++; if(inLR)orangeLR++; }
    if(px>S*0.62 && py>S*0.58){ frN++;
      if(lum>20){ frBloom++; if(r>g&&g>=b) frWarm++; } }
    n++;
  }
  return { canvasW:c.width, nonBlankPct:+(100*nonBlank/n).toFixed(1), voidPurityPct:+(100*voidPx/n).toFixed(1),
    cyanMassPct:+(100*cyan/n).toFixed(1),
    cyanCenterDensityPct:+(100*cyanCenter/Math.max(1,centerN)).toFixed(2),
    orangeAllPct:+(100*orangeAll/n).toFixed(2),
    orangeCenterDensityPct:+(100*orangeCenter/Math.max(1,centerN)).toFixed(2),
    orangeLowerRightDensityPct:+(100*orangeLR/Math.max(1,lrN)).toFixed(2),
    whiteClipPct:+(100*whiteClip/n).toFixed(2),
    fgBokehPct:+(100*frBloom/Math.max(1,frN)).toFixed(1),
    fgWarmPct:+(100*frWarm/Math.max(1,frN)).toFixed(1),
    meanLum:+(lumSum/n).toFixed(1), maxLum:+maxLum.toFixed(0) };
};

const ARCH = { 1:'cyan rim uPow 3.5 (tightest-broad)', 2:'cyan rim uPow 4.0 (mid)', 3:'cyan rim uPow 4.5 (sharpest silhouette)' };
const results = [];
const browser = await chromium.launch({ args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-angle=swiftshader'] });
for (const v of [1,2,3]) {
  const ctx = await browser.newContext({ viewport:{width:1280,height:800} });
  const page = await ctx.newPage();
  await page.addInitScript(() => { const o=HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext=function(t,a){ if(t&&t.indexOf('webgl')===0)a=Object.assign({},a,{preserveDrawingBuffer:true}); return o.call(this,t,a);} ; });
  const errors=[]; page.on('console',m=>{if(m.type()==='error')errors.push(m.text().slice(0,200));});
  page.on('pageerror',e=>errors.push('PE:'+e.message.slice(0,200)));
  const url='file://'+path.join(here,file)+'?v='+v;
  try{ await page.goto(url,{waitUntil:'networkidle',timeout:30000}); }catch(e){ errors.push('GOTO:'+e.message.slice(0,120)); }
  await page.waitForTimeout(6000);
  let a={}; try{ a=await page.evaluate(ANALYZE); }catch(e){ a={error:e.message}; }
  const shot=path.join(outDir,'N75-v'+v+'.png'); try{ await page.screenshot({path:shot}); }catch(e){}
  // three-floor covenant: void>=60 AND orange 3-8 AND cyanMass>=8
  const ok = a && a.voidPurityPct>=60 && a.orangeAllPct>=3 && a.orangeAllPct<=8 && a.cyanMassPct>=8;
  results.push({ variant:'v'+v, arch:ARCH[v], errorCount:errors.length, errors:errors.slice(0,4),
    threeFloorPass: !!ok, analysis:a });
  await ctx.close();
}
await browser.close();
console.log(JSON.stringify(results,null,2));

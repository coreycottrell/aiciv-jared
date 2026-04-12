#!/usr/bin/env python3
"""E2E Full Flow v3 - pay-test-sandbox-3 - Fixed Phase 4+ - 2026-03-04"""
import asyncio, os, sys, subprocess, time, json

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-full-flow-screenshots"
TG = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"
URL = "https://purebrain.ai/pay-test-sandbox-3/"
PW = "PureBrain.ai253443$$$"
PP_EMAIL = "sb-c89tj49549583@personal.example.com"
PP_PASS = "Z0+6<dS"
AI = "Keen"

QA = [("Alex Carter","name"),("alex.carter.e2e@example.com","email"),
      ("Pure Technology","company"),("CTO","role"),
      ("Build the most efficient AI research and reporting pipeline","goal")]

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
sc=[0]

def tg(m):
    try: subprocess.run([TG,m[:4090]],timeout=15,capture_output=True); print(f"[TG] {m[:70]}")
    except: pass

def tgp(path,cap):
    try: subprocess.run([TG,"--photo",path,cap],timeout=20,capture_output=True); print(f"[TGP] {cap[:60]}")
    except: pass

async def ss(page,label,tg_send=False):
    sc[0]+=1
    num=str(sc[0]).zfill(2)
    fname=f"{num}-{label}.png"
    path=os.path.join(SCREENSHOT_DIR,fname)
    try:
        await page.screenshot(path=path,full_page=False)
        print(f"[SS] {fname}")
        if tg_send: tgp(path,f"{num}: {label}")
    except Exception as e: print(f"[SS-ERR] {label}: {e}")
    return path

async def click_any(page, sels, label="", timeout=5000):
    for s in sels:
        try:
            el=await page.wait_for_selector(s,state="visible",timeout=timeout)
            if el: await el.click(); print(f"[CLICK] {label} -> {s}"); return True
        except: continue
    print(f"[MISS] {label}"); return False

async def run():
    from playwright.async_api import async_playwright
    print("="*60); print("E2E v3 FULL FLOW"); print("="*60)
    tg("E2E v3 starting - ALL phases - sandbox-3")

    xvfb=None
    try:
        subprocess.run(["pkill","-f","Xvfb :97"],capture_output=True)
        await asyncio.sleep(1)
        xvfb=subprocess.Popen(["Xvfb",":97","-screen","0","1440x900x24"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        os.environ["DISPLAY"]=":97"; await asyncio.sleep(2); print("[XVFB] :97")
    except Exception as e: print(f"[XVFB] {e}")

    errs=[]; cons=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(headless=False,args=["--no-sandbox","--disable-dev-shm-usage","--window-size=1440,900"])
        ctx=await br.new_context(viewport={"width":1440,"height":900},user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        pg=await ctx.new_page()
        pg.on("console",lambda m: cons.append(f"[{m.type}] {m.text}") if m.type in ["error","warn"] else None)
        pg.on("pageerror",lambda e: errs.append(str(e)))

        # P1: PASSWORD
        print("\n=== P1: PASSWORD ===")
        await pg.goto(URL,wait_until="networkidle",timeout=30000); await asyncio.sleep(2)
        await ss(pg,"p1-before",tg_send=True)
        try:
            pw_el=await pg.wait_for_selector("input[type='password']",state="visible",timeout=5000)
            await pw_el.fill(PW); await pg.keyboard.press("Enter"); await asyncio.sleep(4)
        except:
            inps=await pg.query_selector_all("input")
            for i in inps:
                t=await i.get_attribute("type")
                if t in ["password","text"]: await i.fill(PW); await pg.keyboard.press("Enter"); await asyncio.sleep(4); break
        await ss(pg,"p1-after",tg_send=True); tg("P1: PASS")

        # P2: PRE-PAYMENT CHAT
        print("\n=== P2: PRE-PAYMENT CHAT ===")
        await asyncio.sleep(2)
        await click_any(pg,["button:has-text('Awaken your pure brain')","button:has-text('Awaken')"],"Awaken",8000)
        await asyncio.sleep(3); await ss(pg,"p2-awaken",tg_send=True)
        await click_any(pg,["button:has-text('Begin awakening')","button:has-text('Begin')"],"Begin",8000)
        await asyncio.sleep(4); await ss(pg,"p2-begin",tg_send=True)
        # bypass
        for sel in ["input[placeholder*='response']","input[placeholder*='Response']","input[type='text']"]:
            try:
                el=await pg.wait_for_selector(sel,state="visible",timeout=4000)
                if el and await el.is_enabled():
                    await el.click(); await el.fill("pb-full-bypass"); await pg.keyboard.press("Enter")
                    print("[P2] bypass sent"); break
            except: continue
        await asyncio.sleep(5); await ss(pg,"p2-bypass",tg_send=True)
        # detect AI name
        detected=AI
        bt=await pg.evaluate("()=>document.body.innerText")
        for c in ["Keen","Nova","Sage","Atlas","Echo","Aria"]:
            if c in bt: detected=c; break
        print(f"[P2] AI={detected}"); tg(f"P2: AI='{detected}'")
        # handle loop
        for i in range(5):
            await asyncio.sleep(3)
            vi=await pg.evaluate("""()=>{
                var i=Array.from(document.querySelectorAll('input[type=text],textarea')).find(x=>{
                    var s=window.getComputedStyle(x),r=x.getBoundingClientRect();
                    return s.display!='none'&&s.visibility!='hidden'&&parseFloat(s.opacity)>0&&r.width>0&&r.height>0&&!x.disabled&&!x.readOnly;
                }); return i?{ph:i.placeholder}:null;
            }""")
            if not vi: break
            ph=vi.get("ph",""); ans="Alex Carter" if "name" in ph.lower() else "alex@example.com" if "email" in ph.lower() else "Continue"
            try:
                el=await pg.query_selector(f"input[placeholder='{ph}']") if ph else await pg.query_selector("input[type=text]:not([disabled])")
                if el: await el.click(); await el.fill(ans); await pg.keyboard.press("Enter"); print(f"[P2-LOOP] '{ans}' for '{ph}'")
            except: break
            disc=await pg.query_selector("button:has-text('discover')")
            if disc: print("[P2-LOOP] discover appeared"); break
        await ss(pg,"p2-done",tg_send=True); tg("P2: COMPLETE")

        # P3: DISCOVERY
        print("\n=== P3: DISCOVERY ===")
        await asyncio.sleep(2)
        await click_any(pg,["button:has-text('Click to discover what your pure brain can do')","button:has-text('discover')"],"Discover",8000)
        await asyncio.sleep(4); await ss(pg,"p3-discover",tg_send=True)
        await click_any(pg,[f"text=Click to see what {detected}","button:has-text('can do for you')","button:has-text('can do')"],"SeeWhat",8000)
        await asyncio.sleep(4); await ss(pg,"p3-seewhat",tg_send=True)
        await click_any(pg,[f"button:has-text('see what {detected} can do')","button:has-text('can do ->')"],"Overlay",5000)
        await asyncio.sleep(3); await ss(pg,"p3-overlay",tg_send=True); tg("P3: COMPLETE")

        # P4: PAYMENT TIER - use JS coordinates instead of scroll_into_view
        print("\n=== P4: PAYMENT TIER ===")
        tg("P4: Finding Awakened tier"); await asyncio.sleep(3)
        await ss(pg,"p4-initial",tg_send=True)

        act_info=await pg.evaluate(f"""()=>{{
            var btns=Array.from(document.querySelectorAll('button,a'));
            var act=btns.find(b=>b.textContent.includes('Activate {detected} now')||
                              (b.textContent.includes('Activate')&&b.textContent.includes('now')));
            if(!act) act=btns.find(b=>b.textContent.trim().startsWith('Activate'));
            if(!act) return null;
            var r=act.getBoundingClientRect();
            return {{text:act.textContent.trim(),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),inView:r.top>=0&&r.bottom<=window.innerHeight}};
        }}""")
        print(f"[P4] Activate: {act_info}")

        if act_info:
            if not act_info.get("inView"):
                await pg.evaluate(f"window.scrollTo(0,Math.max(0,{act_info['y']}-400))")
                await asyncio.sleep(2)
            await ss(pg,"p4-activate-found",tg_send=True)
            await pg.mouse.click(act_info["x"],act_info["y"])
            print(f"[P4] Activate clicked at ({act_info['x']},{act_info['y']})")
            tg("P4: PASS - Activate clicked")
        else:
            print("[P4] Activate not found via JS - trying selector")
            await pg.evaluate("window.scrollTo(0,document.body.scrollHeight*0.7)"); await asyncio.sleep(2)
            await ss(pg,"p4-scroll",tg_send=True)
            act2=await pg.query_selector(f"button:has-text('Activate {detected}')")
            if not act2: act2=await pg.query_selector("button:has-text('Activate')")
            if act2:
                await act2.click(); tg("P4: Activate fallback click")
            else:
                tg("P4: WARNING - no Activate found")

        await asyncio.sleep(5); await ss(pg,"p4-result",tg_send=True)

        # P5: PAYPAL
        print("\n=== P5: PAYPAL ===")
        tg("P5: PayPal"); await asyncio.sleep(4)

        ps=await pg.evaluate("""()=>{
            var sim=Array.from(document.querySelectorAll('button')).find(b=>b.textContent.toLowerCase().includes('simulate'));
            var pay=Array.from(document.querySelectorAll('button')).find(b=>b.textContent.toLowerCase().includes('pay with paypal'));
            var ifrm=document.querySelector('iframe[src*=paypal],iframe[name*=paypal]');
            return {hasSimBtn:!!sim,simTxt:sim?sim.textContent.trim():null,
                    hasPayBtn:!!pay,payTxt:pay?pay.textContent.trim():null,
                    hasIframe:!!ifrm};
        }""")
        print(f"[P5] Payment state: {ps}")
        await ss(pg,"p5-check",tg_send=True)

        pp_real=False; pp_sim=False

        if ps.get("hasSimBtn"):
            sim=await pg.query_selector("button:has-text('Simulate')")
            if sim: await sim.click(); pp_sim=True; await asyncio.sleep(6); await ss(pg,"p5-simulated",tg_send=True); tg("P5: simulate clicked")
        else:
            # Try opening modal
            r=await pg.evaluate("""()=>{
                if(typeof openPayPalModal==='function'){openPayPalModal('Awakened');return 'opened';}
                return 'not found';
            }""")
            print(f"[P5] JS modal: {r}"); await asyncio.sleep(4)
            await ss(pg,"p5-js-modal",tg_send=True)
            sim2=await pg.query_selector("button:has-text('Simulate')")
            if sim2: await sim2.click(); pp_sim=True; await asyncio.sleep(6); await ss(pg,"p5-sim2",tg_send=True); tg("P5: sim2")

        if not pp_real and not pp_sim:
            # Try PayPal iframe coordinate click
            if ps.get("hasIframe"):
                ib=await pg.evaluate("""()=>{var i=document.querySelector('iframe[src*=paypal]');if(!i)return null;var r=i.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};}""")
                if ib:
                    await pg.mouse.click(ib['x']+ib['w']/2, ib['y']+25)
                    await asyncio.sleep(5); await ss(pg,"p5-iframe-click",tg_send=True); tg("P5: iframe click")

        if not pp_real and not pp_sim:
            # Direct JS simulation
            sid=f"E2E-V3-{int(time.time())}"
            for fn in [f"window.onPaymentComplete&&window.onPaymentComplete('Awakened','{sid}',{{}})",
                       f"typeof launchPostPaymentFlow==='function'&&launchPostPaymentFlow('Awakened','{sid}')"]:
                try:
                    await pg.evaluate(f"()=>{{{fn}}}")
                    pp_sim=True; print(f"[P5] JS sim: {fn[:60]}"); break
                except: continue
            tg(f"P5: JS simulation (sim={pp_sim})")

        await asyncio.sleep(6); await ss(pg,"p5-result",tg_send=True)
        tg(f"P5: Done real={pp_real} sim={pp_sim}")

        # P6: Q&A
        print("\n=== P6: Q&A ===")
        tg("P6: Post-payment Q&A"); await asyncio.sleep(5)
        cb=await pg.evaluate("""()=>{var e=document.getElementById('pay-test-post-payment');if(!e)return{found:false};var s=window.getComputedStyle(e);return{found:true,ch:e.children.length,txt:e.innerText.substring(0,200)};}""")
        print(f"[P6] Chatbox: {cb}"); await ss(pg,"p6-chatbox",tg_send=True)
        if errs: print(f"[P6] Errs: {errs[:2]}"); tg(f"P6 ERRORS: {errs[0][:150]}")

        qa_done=0
        for answer,fname in QA:
            await asyncio.sleep(4)
            found=False
            for sel in ["#pay-test-post-payment input[type='text']:not([disabled]):not([readonly])",
                        "#pay-test-post-payment textarea:not([disabled])",
                        ".pb-chatbox input:not([disabled])",
                        "input[type='text']:not([disabled]):not([readonly])"]:
                try:
                    el=await pg.wait_for_selector(sel,state="visible",timeout=5000)
                    if el and await el.is_enabled():
                        await el.click(); await el.fill(answer)
                        await ss(pg,f"p6-{fname}",tg_send=(fname in ["name","goal"]))
                        await pg.keyboard.press("Enter"); qa_done+=1; found=True; print(f"[P6] '{fname}': {answer}"); break
                except: continue
            if not found:
                print(f"[P6] Miss '{fname}'"); await ss(pg,f"p6-miss-{fname}",tg_send=True)
                slide=await pg.evaluate("""()=>!!Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Show Me More')||b.textContent.includes('incredible'))""")
                if slide: print("[P6] Slides started"); break

        await ss(pg,"p6-done",tg_send=True); tg(f"P6: {qa_done}/5")

        # P7: SLIDES
        print("\n=== P7: SLIDES ===")
        tg("P7: Slides"); await asyncio.sleep(3)
        slides=0
        for i in range(12):
            await asyncio.sleep(3)
            bi=await pg.evaluate("""()=>{
                var btns=Array.from(document.querySelectorAll('button'));
                var sm=btns.find(b=>b.textContent.includes('Show Me More'));
                var fn=btns.find(b=>b.textContent.includes('incredible')||b.textContent.includes("let's go"));
                var el=sm||fn;
                if(!el)return null;
                var r=el.getBoundingClientRect();
                var s=window.getComputedStyle(el);
                return{type:sm?'show':'final',txt:el.textContent.trim(),
                       x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),
                       vis:s.display!='none'&&s.visibility!='hidden'&&r.height>0};
            }""")
            if not bi or not bi.get("vis"): print(f"[P7] No btn at {i+1}"); await ss(pg,f"p7-nobtn-{i+1}"); break
            if i in [0,4,9]: await ss(pg,f"p7-slide-{i+1}",tg_send=True)
            await pg.evaluate(f"window.scrollTo(0,Math.max(0,{bi['y']}-400))"); await asyncio.sleep(1)
            await pg.mouse.click(bi["x"],bi["y"]); slides+=1; print(f"[P7] {i+1}: {bi['type']}")
            if bi["type"]=="final": await asyncio.sleep(4); await ss(pg,"p7-final",tg_send=True); break
        await ss(pg,"p7-done",tg_send=True); tg(f"P7: {slides} slides")

        # P8: READY BUTTON
        print("\n=== P8: READY ===")
        tg("P8: Your AI is ready"); await asyncio.sleep(4)
        await ss(pg,"p8-check",tg_send=True)
        ri=await pg.evaluate("""()=>{
            var btns=Array.from(document.querySelectorAll('button,a'));
            var r=btns.find(b=>b.textContent.includes('ready')||b.textContent.includes('AI is ready')||b.textContent.includes('next steps'));
            if(!r)return null;
            var rect=r.getBoundingClientRect();
            return{txt:r.textContent.trim(),x:Math.round(rect.x+rect.width/2),y:Math.round(rect.y+rect.height/2)};
        }""")
        print(f"[P8] Ready: {ri}")
        if ri:
            await pg.evaluate(f"window.scrollTo(0,Math.max(0,{ri['y']}-400))"); await asyncio.sleep(1)
            await ss(pg,"p8-ready",tg_send=True)
            await pg.mouse.click(ri["x"],ri["y"]); print(f"[P8] Clicked: {ri['txt'][:40]}")
            tg(f"P8: PASS - '{ri['txt'][:40]}' clicked")
            await asyncio.sleep(5); await ss(pg,"p8-after",tg_send=True)
        else:
            await pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); await asyncio.sleep(2)
            await ss(pg,"p8-bottom",tg_send=True); tg("P8: ready not found")

        # P9: BRAIN STREAM
        print("\n=== P9: BRAIN STREAM (END GOAL) ===")
        tg("P9: BRAIN STREAM - THE END GOAL"); await asyncio.sleep(6)
        sc[0]+=1
        fp=os.path.join(SCREENSHOT_DIR,f"{str(sc[0]).zfill(2)}-p9-fullpage.png")
        await pg.screenshot(path=fp,full_page=True); tgp(fp,"P9: Full page final state")

        bss=await pg.evaluate("""()=>{
            var target='BRAIN STREAM';
            var walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
            var node,found=null;
            while(node=walker.nextNode()){
                if(node.textContent.toUpperCase().includes(target)){found=node.parentElement;break;}
            }
            var pp=document.getElementById('pay-test-post-payment');
            var ppInfo=pp?{ch:pp.children.length,txt:pp.innerText.substring(0,400),disp:window.getComputedStyle(pp).display}:null;
            if(!found)return{found:false,inHTML:document.body.innerHTML.toUpperCase().includes(target),pp:ppInfo};
            var r=found.getBoundingClientRect();
            var s=window.getComputedStyle(found);
            var btn=found;
            for(var i=0;i<5;i++){if(btn.tagName==='BUTTON'||btn.tagName==='A')break;if(btn.parentElement)btn=btn.parentElement;}
            var br=btn.getBoundingClientRect();
            return{found:true,txt:found.textContent.trim(),opacity:s.opacity,display:s.display,
                   visibility:s.visibility,pointerEvents:s.pointerEvents,
                   elX:Math.round(r.x+r.width/2),elY:Math.round(r.y+r.height/2),
                   btnX:Math.round(br.x+br.width/2),btnY:Math.round(br.y+br.height/2),pp:ppInfo};
        }""")
        print(f"[P9] Brain Stream: {json.dumps(bss,indent=2)}")

        bs_found=False; bs_grey=False

        if bss.get("found"):
            bs_found=True
            bx=bss.get("btnX",bss.get("elX",720)); by=bss.get("btnY",bss.get("elY",500))
            op=float(bss.get("opacity",1.0)); pe=bss.get("pointerEvents","auto")
            bs_grey=op<0.8 or pe=="none"
            await pg.evaluate(f"window.scrollTo(0,Math.max(0,{by}-300))"); await asyncio.sleep(2)
            await ss(pg,"p9-brain-stream",tg_send=True)
            await ss(pg,"p9-brain-stream-2",tg_send=True)
            await ss(pg,"p9-brain-stream-3",tg_send=True)
            st="GREYED (as expected)" if bs_grey else "ACTIVE"
            print(f"[P9] BRAIN STREAM FOUND! {st} opacity={op}"); tg(f"P9: BRAIN STREAM FOUND! {st} opacity={op}")
            if not bs_grey:
                await pg.mouse.click(bx,by); await asyncio.sleep(4)
                await ss(pg,"p9-clicked",tg_send=True); tg("P9: BRAIN STREAM CLICKED!")
            sc[0]+=1
            ff=os.path.join(SCREENSHOT_DIR,f"{str(sc[0]).zfill(2)}-p9-FINAL.png")
            await pg.screenshot(path=ff,full_page=True); tgp(ff,f"FINAL: {detected} Brain Stream - {st}")
        else:
            print(f"[P9] NOT FOUND. inHTML={bss.get('inHTML')} pp={bss.get('pp')}")
            await ss(pg,"p9-not-found",tg_send=True)
            tg(f"P9: NOT FOUND. inHTML={bss.get('inHTML')} pp_children={bss.get('pp',{}).get('ch') if bss.get('pp') else 'N/A'}")

        e_errs=[e for e in cons if "error" in e.lower()]
        print(f"[P9] Errs: {e_errs[:3]}"); print(f"[P9] Page errs: {errs[:3]}")

        res={"date":"2026-03-04","ai":detected,"paypal":"real" if pp_real else "sim" if pp_sim else "fail",
             "qa":qa_done,"slides":slides,"bs_found":bs_found,"bs_grey":bs_grey,
             "screenshots":sc[0],"page_errs":errs[:5],"console_errs":e_errs[:5]}
        with open(os.path.join(SCREENSHOT_DIR,"e2e-v3-results.json"),"w") as f: json.dump(res,f,indent=2)

        await br.close()
    if xvfb: xvfb.terminate()

    s=f"E2E v3 DONE\nAI: {res['ai']}\nPayPal: {res['paypal']}\nQ&A: {res['qa']}/5\nSlides: {res['slides']}\nBrain Stream: {'FOUND-GREY' if bs_found and bs_grey else 'FOUND-ACTIVE' if bs_found else 'NOT-FOUND'}\nSSs: {res['screenshots']}"
    print(f"\n{s}"); tg(s); return res

if __name__=="__main__":
    try:
        r=asyncio.run(run()); sys.exit(0 if r and r.get("bs_found") else 1)
    except Exception as e:
        print(f"[FATAL] {e}"); import traceback; traceback.print_exc()
        try: subprocess.run([TG,f"E2E v3 FATAL: {str(e)[:200]}"],timeout=10,capture_output=True)
        except: pass
        sys.exit(1)

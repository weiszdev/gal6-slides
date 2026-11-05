"""Headless sync test: presenter + wide + vert pages in one browser context. Run: /workspace/venv-pw/bin/python test_sync.py"""
import asyncio, os, sys, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROME = "/usr/bin/google-chrome"

async def cur(page):
    # which slide the view page shows (from <img src>) and black state
    return await page.evaluate("[document.getElementById('s').getAttribute('src'), document.getElementById('blk').style.display]")

async def run(base, label, no_bc=False):
    results = []
    def check(name, ok, info=""):
        results.append(ok); print(("PASS " if ok else "FAIL ") + f"[{label}] {name} {info}")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=["--no-sandbox", "--allow-file-access-from-files"] if False else ["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1280, "height": 800})
        if no_bc: await ctx.add_init_script("delete window.BroadcastChannel;")
        errs = []
        pres, wide, vert = await ctx.new_page(), await ctx.new_page(), await ctx.new_page()
        for pg in (pres, wide, vert): pg.on("pageerror", lambda e: errs.append(str(e)))
        await pres.goto(base + "presenter.html"); await wide.goto(base + "wide.html"); await vert.goto(base + "vert.html")
        await pres.wait_for_timeout(500)
        check("initial slide 1", (await cur(wide))[0] == "wide/01.png" and (await cur(vert))[0] == "vert/01.png", str(await cur(wide)))
        await pres.bring_to_front(); await pres.keyboard.press("ArrowRight"); await pres.wait_for_timeout(700)
        check("ArrowRight -> 02 on both", (await cur(wide))[0] == "wide/02.png" and (await cur(vert))[0] == "vert/02.png", f"{await cur(wide)} {await cur(vert)}")
        await pres.keyboard.press("Space"); await pres.keyboard.press("PageDown"); await pres.wait_for_timeout(700)
        check("Space+PageDown -> 04", (await cur(wide))[0] == "wide/04.png" and (await cur(vert))[0] == "vert/04.png")
        await pres.keyboard.press("ArrowLeft"); await pres.wait_for_timeout(700)
        check("ArrowLeft -> 03", (await cur(wide))[0] == "wide/03.png" and (await cur(vert))[0] == "vert/03.png")
        await pres.click("#cw"); await pres.wait_for_timeout(700)
        check("click current slide -> 04", (await cur(wide))[0] == "wide/04.png")
        await pres.keyboard.press("b"); await pres.wait_for_timeout(700)
        check("B -> black on both", (await cur(wide))[1] == "block" and (await cur(vert))[1] == "block")
        await pres.keyboard.press("b"); await pres.wait_for_timeout(700)
        check("B again -> visible", (await cur(wide))[1] == "none" and (await cur(vert))[1] == "none")
        await pres.keyboard.press("End"); await pres.wait_for_timeout(700)
        check("End -> 35", (await cur(wide))[0] == "wide/35.png" and (await cur(vert))[0] == "vert/35.png")
        await pres.keyboard.press("ArrowRight"); await pres.wait_for_timeout(200)
        check("clamped at 35", (await cur(wide))[0] == "wide/35.png")
        await pres.keyboard.press("Home"); await pres.wait_for_timeout(700)
        # control from the view window itself
        await wide.bring_to_front(); await wide.keyboard.press("ArrowRight"); await pres.wait_for_timeout(700)
        check("key on wide window drives vert + presenter", (await cur(vert))[0] == "vert/02.png" and "2 / 35" in await pres.inner_text("#num"), await pres.inner_text("#num"))
        # go-to box
        await pres.bring_to_front(); await pres.fill("#gt", "20"); await pres.click("#bg"); await pres.wait_for_timeout(700)
        check("Go to 20", (await cur(wide))[0] == "wide/20.png" and (await cur(vert))[0] == "vert/20.png")
        # presenter shows next thumbnails and sync dots
        nxt = await pres.evaluate("[document.getElementById('nw').getAttribute('src'), document.getElementById('nv').getAttribute('src')]")
        check("presenter next thumbs", nxt == ["wide/21.png", "vert/21.png"], str(nxt))
        await pres.wait_for_timeout(1500)
        dots = await pres.evaluate("[document.getElementById('dw').className, document.getElementById('dv').className]")
        check("presenter sees wide+vert connected", all("on" in d for d in dots), str(dots))
        # ?slide=N on a late-joining window, and others follow
        late = await ctx.new_page(); await late.goto(base + "vert.html?slide=9"); await late.wait_for_timeout(500)
        check("?slide=9 shows 09 and others follow", (await cur(late))[0] == "vert/09.png" and (await cur(wide))[0] == "wide/09.png", f"{await cur(late)} {await cur(wide)}")
        # late joiner with no param adopts stored state
        late2 = await ctx.new_page(); await late2.goto(base + "wide.html"); await late2.wait_for_timeout(500)
        check("late joiner adopts current slide 09", (await cur(late2))[0] == "wide/09.png")
        # ?key=1 serves the green-key set and stays in sync
        kw = await ctx.new_page(); await kw.goto(base + "wide.html?key=1"); await kw.wait_for_timeout(700)
        check("?key=1 wide uses wide_key/ and follows slide", (await cur(kw))[0] == "wide_key/09.png", str(await cur(kw)))
        kv = await ctx.new_page(); await kv.goto(base + "vert.html?key=1"); await kv.wait_for_timeout(700)
        await pres.bring_to_front(); await pres.keyboard.press("ArrowRight"); await pres.wait_for_timeout(700)
        check("key pages follow presenter", (await cur(kw))[0] == "wide_key/10.png" and (await cur(kv))[0] == "vert_key/10.png" and (await cur(wide))[0] == "wide/10.png", f"{await cur(kw)} {await cur(kv)}")
        # timer starts on first advance
        t0 = await pres.inner_text("#tm"); 
        check("no JS errors", not errs, str(errs))
        await b.close()
    return all(results)

def main():
    ok = True
    # 1) served over http
    srv = subprocess.Popen([sys.executable, "-m", "http.server", "8766", "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        ok &= asyncio.run(run("http://127.0.0.1:8766/", "http+BroadcastChannel"))
        ok &= asyncio.run(run("http://127.0.0.1:8766/", "http, BroadcastChannel removed (localStorage fallback)", no_bc=True))
    finally:
        srv.terminate()
    # 2) opened as local files
    ok &= asyncio.run(run("file://" + ROOT + "/", "file://+BroadcastChannel"))
    ok &= asyncio.run(run("file://" + ROOT + "/", "file://, BroadcastChannel removed (localStorage fallback)", no_bc=True))
    print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
main()

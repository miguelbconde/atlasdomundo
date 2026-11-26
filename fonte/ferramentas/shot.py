import asyncio,sys,os
from playwright.async_api import async_playwright
# uso: python3 fonte/ferramentas/shot.py <rota sem #> <nome> [largura altura] ["js"]  -> /tmp/<nome>.png
# exige o servidor de teste: python3 -m http.server 8765 --directory web
async def m():
    h,n=sys.argv[1],sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 1366; hh=int(sys.argv[4]) if len(sys.argv)>4 else 900
    js=sys.argv[5] if len(sys.argv)>5 else None
    async with async_playwright() as p:
        b=await (p.chromium.launch(executable_path="/usr/bin/google-chrome") if os.path.exists("/usr/bin/google-chrome") else p.chromium.launch());e=[]
        pg=await b.new_page(viewport={'width':w,'height':hh});pg.on('pageerror',lambda x:e.append(str(x)))
        await pg.goto("http://localhost:8765/index.html#"+h);await pg.wait_for_timeout(1800)
        if js: await pg.evaluate(js); await pg.wait_for_timeout(800)
        await pg.screenshot(path=f'/tmp/{n}.png'); print('ERR',e); await b.close()
asyncio.run(m())

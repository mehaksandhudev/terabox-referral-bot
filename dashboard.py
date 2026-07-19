"""
TeraBox Referral Automation - Dashboard Server
Run: python dashboard.py | Open: http://localhost:8080
"""

import http.server
import socketserver
import json
import os
import threading
import requests
import time

PORT = int(os.environ.get("PORT", 8080))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(SCRIPT_DIR, "stats.json")
LINKS_FILE = os.path.join(SCRIPT_DIR, "referral_links.txt")
LOGS_FILE = os.path.join(SCRIPT_DIR, "logs.json")
CONTROL_FILE = os.path.join(SCRIPT_DIR, "control.json")

DEFAULT_CONTROL = {"paused": False, "stopped": False, "round_delay": 30, "link_delay": 15, "telegram_token": "", "telegram_chat_id": ""}

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TeraBox Automation</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#09090b;--surface:#18181b;--surface2:#27272a;--border:#3f3f46;--border-s:#27272a;--text:#fafafa;--text2:#a1a1aa;--muted:#71717a;--accent:#6366f1;--green:#22c55e;--red:#ef4444;--amber:#eab308;--r:8px}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-size:14px}
.app{max-width:1400px;margin:0 auto;padding:24px 32px}

.hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;padding-bottom:16px;border-bottom:1px solid var(--border-s)}
.hdr h1{font-size:18px;font-weight:700;letter-spacing:-.3px}
.hdr h1 span{color:var(--muted);font-weight:400}
.st{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%}
.dot.idle{background:var(--muted)}.dot.run{background:var(--green);box-shadow:0 0 8px rgba(34,197,94,.4);animation:b 1.5s infinite}.dot.done{background:var(--accent)}.dot.paused{background:var(--amber);animation:b 2s infinite}.dot.stopped{background:var(--red)}
@keyframes b{0%,100%{opacity:1}50%{opacity:.4}}

.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.s{background:var(--surface);border:1px solid var(--border-s);border-radius:var(--r);padding:16px 20px}
.s-l{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;font-weight:600}
.s-v{font-size:28px;font-weight:700;font-variant-numeric:tabular-nums}
.s-v.bl{color:var(--accent)}.s-v.gr{color:var(--green)}.s-v.rd{color:var(--red)}.s-v.mt{color:var(--text2)}

.prog{display:flex;align-items:center;gap:14px;margin-bottom:20px}
.prog-bar{flex:1;height:4px;background:var(--surface2);border-radius:4px;overflow:hidden}
.prog-fill{height:100%;background:var(--accent);border-radius:4px;transition:width .6s ease}
.prog-lbl{font-size:12px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}

/* Controls Bar */
.ctrl{display:flex;align-items:center;gap:12px;margin-bottom:20px;padding:14px 18px;background:var(--surface);border:1px solid var(--border-s);border-radius:var(--r);flex-wrap:wrap}
.ctrl-label{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);font-weight:600}
.ctrl-sep{width:1px;height:28px;background:var(--border-s);margin:0 4px}
.ctrl-group{display:flex;align-items:center;gap:8px}
.ctrl-input{width:60px;padding:6px 8px;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:12px;text-align:center;outline:none}
.ctrl-input:focus{border-color:var(--accent)}
.ctrl-unit{font-size:11px;color:var(--muted)}

.p{background:var(--surface);border:1px solid var(--border-s);border-radius:var(--r);overflow:hidden;margin-bottom:16px}
.p-h{padding:12px 18px;border-bottom:1px solid var(--border-s);display:flex;align-items:center;justify-content:space-between}
.p-h h2{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--text2)}
.p-h .bg{font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace}
.p-b{padding:14px 18px}

.add-row{display:flex;gap:10px;margin-bottom:12px}
.add-row input{flex:1;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:'Inter',sans-serif;font-size:13px;outline:none;transition:border-color .2s}
.add-row input:focus{border-color:var(--accent)}
.add-row input::placeholder{color:var(--muted)}
.btn{padding:9px 16px;border:none;border-radius:6px;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s}
.btn-p{background:var(--accent);color:#fff}.btn-p:hover{opacity:.85}
.btn-green{background:var(--green);color:#fff}.btn-green:hover{opacity:.85}
.btn-amber{background:var(--amber);color:#000}.btn-amber:hover{opacity:.85}
.btn-red{background:var(--red);color:#fff}.btn-red:hover{opacity:.85}
.btn-sm{padding:4px 8px;font-size:11px;border-radius:4px}
.btn-g{background:transparent;color:var(--muted);border:1px solid var(--border)}.btn-g:hover{color:var(--red);border-color:var(--red)}

.ll{list-style:none;max-height:180px;overflow-y:auto}
.ll::-webkit-scrollbar{width:3px}.ll::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.li{display:flex;align-items:center;justify-content:space-between;padding:7px 8px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--text2)}
.li:hover{background:var(--surface2)}
.li-i{color:var(--muted);margin-right:8px;min-width:18px}
.li-u{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lf{display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:1px solid var(--border-s);margin-top:10px}
.lf span{font-size:12px;color:var(--muted)}

.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:9px 18px;font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);font-weight:600;border-bottom:1px solid var(--border-s);background:rgba(0,0,0,.2)}
td{padding:9px 18px;font-size:13px;border-bottom:1px solid var(--border-s);color:var(--text2)}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.02)}
.mono{font-family:'JetBrains Mono',monospace;font-size:12px}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.t-ok{background:rgba(34,197,94,.1);color:var(--green)}
.t-err{background:rgba(239,68,68,.1);color:var(--red)}
.t-run{background:rgba(234,179,8,.1);color:var(--amber)}
.empty{text-align:center;padding:32px;color:var(--muted);font-size:13px}

.log-v{max-height:340px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:11.5px;line-height:1.8;padding:2px 0}
.log-v::-webkit-scrollbar{width:3px}.log-v::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.log-l{padding:1px 0;color:var(--muted)}
.log-l .ts{color:var(--muted);opacity:.6}
.log-l .INFO{color:var(--text2)}
.log-l .WARNING{color:var(--amber)}
.log-l .ERROR,.log-l .CRITICAL{color:var(--red)}

.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.toast{position:fixed;bottom:24px;right:24px;padding:10px 16px;border-radius:6px;font-size:13px;font-weight:500;z-index:100;transform:translateY(80px);opacity:0;transition:all .25s;background:var(--surface2);color:var(--text);border:1px solid var(--border)}
.toast.show{transform:translateY(0);opacity:1}
.tg-group{display:flex;flex-direction:column;gap:12px;padding:14px 18px}
.tg-field{display:flex;flex-direction:column;gap:6px}
.tg-field label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--text2)}
.tg-input{width:100%;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:'Inter',sans-serif;font-size:13px;outline:none;transition:border-color .2s}
.tg-input:focus{border-color:var(--accent)}
.tg-input::placeholder{color:var(--muted)}
@media(max-width:900px){.cols{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.app{padding:16px}.ctrl{flex-direction:column;align-items:flex-start}.ctrl-sep{display:none}}
</style>
</head>
<body>
<div class="app">
  <div class="hdr">
    <h1>TeraBox Automation <span>/ Dashboard</span></h1>
    <div class="st"><span class="dot idle" id="dot"></span><span id="stLbl">Idle</span></div>
  </div>

  <!-- Controls Bar -->
  <div class="ctrl">
    <div class="ctrl-group">
      <button class="btn btn-green btn-sm" id="btnResume" onclick="ctrlAction('resume')">Resume</button>
      <button class="btn btn-amber btn-sm" id="btnPause" onclick="ctrlAction('pause')">Pause</button>
      <button class="btn btn-red btn-sm" id="btnStop" onclick="ctrlAction('stop')">Stop</button>
    </div>
    <div class="ctrl-sep"></div>
    <div class="ctrl-group">
      <span class="ctrl-label">Link delay</span>
      <input type="number" class="ctrl-input" id="linkDelay" value="15" min="1" max="300" onchange="saveDelays()">
      <span class="ctrl-unit">sec</span>
    </div>
    <div class="ctrl-sep"></div>
    <div class="ctrl-group">
      <span class="ctrl-label">Round delay</span>
      <input type="number" class="ctrl-input" id="roundDelay" value="30" min="5" max="600" onchange="saveDelays()">
      <span class="ctrl-unit">sec</span>
    </div>
  </div>

  <div class="stats">
    <div class="s"><div class="s-l">Processed</div><div class="s-v bl" id="vT">0</div></div>
    <div class="s"><div class="s-l">Success</div><div class="s-v gr" id="vS">0</div></div>
    <div class="s"><div class="s-l">Errors</div><div class="s-v rd" id="vE">0</div></div>
    <div class="s"><div class="s-l">Rate</div><div class="s-v mt" id="vR">--</div></div>
  </div>

  <div class="prog">
    <div class="prog-bar"><div class="prog-fill" id="pF" style="width:0"></div></div>
    <div class="prog-lbl" id="pL">0 / 0</div>
  </div>

  <div class="cols">
    <div>
      <div class="p">
        <div class="p-h"><h2>Referral Links</h2><span class="bg" id="lC">0</span></div>
        <div class="p-b">
          <div class="add-row">
            <input type="text" id="uI" placeholder="Paste referral URL..." />
            <button class="btn btn-p" onclick="addL()">Add</button>
          </div>
          <ul class="ll" id="lL"></ul>
          <div class="lf" id="lF" style="display:none"><span id="lT">0 links</span><button class="btn btn-sm btn-g" onclick="clrL()">Clear all</button></div>
        </div>
      </div>
      <div class="p">
        <div class="p-h"><h2>Results</h2></div>
        <div class="tw">
          <table><thead><tr><th>#</th><th>URL</th><th>Email</th><th>Status</th><th>Time</th></tr></thead>
          <tbody id="rB"><tr><td colspan="5" class="empty">No results yet</td></tr></tbody></table>
        </div>
      </div>
    </div>
    <div>
      <div class="p">
        <div class="p-h"><h2>Telegram Integration</h2></div>
        <div class="tg-group">
          <div class="tg-field">
            <label>Bot Token</label>
            <input type="text" class="tg-input" id="tgToken" placeholder="Paste bot token (e.g. 123456:ABC...)" />
          </div>
          <div class="tg-field">
            <label>Allowed Chat ID (Optional)</label>
            <input type="text" class="tg-input" id="tgChatId" placeholder="e.g. 123456789" />
          </div>
          <div style="display:flex; gap:10px;">
            <button class="btn btn-p" onclick="saveTelegram()" style="flex:1;">Save Settings</button>
            <button class="btn btn-g" onclick="testTelegram()" style="flex:1;">Test Connection</button>
          </div>
        </div>
      </div>
      <div class="p">
        <div class="p-h"><h2>Live Logs</h2><span class="bg" id="lgC">0 entries</span></div>
        <div class="p-b" style="padding:8px 14px">
          <div class="log-v" id="lgV">
            <div class="log-l" style="color:var(--muted)">Waiting for automation...</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.className='toast show';setTimeout(()=>t.classList.remove('show'),2500)}

// Control
async function ctrlAction(action){
  const body={};
  if(action==='pause') body.paused=true;
  else if(action==='resume'){body.paused=false;body.stopped=false}
  else if(action==='stop') body.stopped=true;
  const r=await fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(r.ok) toast(action==='pause'?'Paused':action==='stop'?'Stop signal sent':'Resumed');
}
async function saveDelays(){
  const ld=parseInt(document.getElementById('linkDelay').value)||15;
  const rd=parseInt(document.getElementById('roundDelay').value)||30;
  await fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({link_delay:ld,round_delay:rd})});
  toast('Delays updated');
}
async function loadCtrl(){
  try{const r=await fetch('/api/control');const d=await r.json();
  document.getElementById('linkDelay').value=d.link_delay||15;
  document.getElementById('roundDelay').value=d.round_delay||30;
  document.getElementById('tgToken').value=d.telegram_token||'';
  document.getElementById('tgChatId').value=d.telegram_chat_id||'';
  }catch{}
}
async function saveTelegram(){
  const token=document.getElementById('tgToken').value.trim();
  const chatId=document.getElementById('tgChatId').value.trim();
  const r=await fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_token:token,telegram_chat_id:chatId})});
  if(r.ok) toast('Telegram settings saved');
}
async function testTelegram(){
  const token=document.getElementById('tgToken').value.trim();
  const chatId=document.getElementById('tgChatId').value.trim();
  if(!token || !chatId){
    toast('Token and Chat ID are required to test');
    return;
  }
  toast('Sending test message...');
  try {
    const r=await fetch('/api/telegram/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_token:token,telegram_chat_id:chatId})});
    const d=await r.json();
    if(d.success) toast('Test message sent! Check Telegram.');
    else toast('Test failed: ' + d.error);
  } catch(e) {
    toast('Error sending test message');
  }
}
loadCtrl();

// Links
async function getL(){try{const r=await fetch('/api/links');return(await r.json()).links||[]}catch{return[]}}
function drawL(ls){
  const l=document.getElementById('lL'),f=document.getElementById('lF'),c=document.getElementById('lC'),t=document.getElementById('lT');
  c.textContent=ls.length;t.textContent=ls.length+' link'+(ls.length!==1?'s':'');f.style.display=ls.length?'flex':'none';
  if(!ls.length){l.innerHTML='<li class="li" style="justify-content:center;color:var(--muted)">No links added</li>';return}
  l.innerHTML=ls.map((u,i)=>`<li class="li"><span class="li-i">${i+1}</span><span class="li-u">${u}</span><button class="btn btn-sm btn-g" onclick="delL(${i})">&times;</button></li>`).join('');
}
async function addL(){
  const inp=document.getElementById('uI'),url=inp.value.trim();
  if(!url||!url.startsWith('http')){toast('Enter a valid URL');return}
  const r=await fetch('/api/links',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
  const d=await r.json();if(d.success){inp.value='';toast('Link added');drawL(d.links)}else toast(d.error||'Failed')
}
async function delL(i){const r=await fetch('/api/links',{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:i})});const d=await r.json();if(d.success)drawL(d.links)}
async function clrL(){if(!confirm('Clear all?'))return;const r=await fetch('/api/links',{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({clear_all:true})});const d=await r.json();if(d.success)drawL(d.links)}
document.getElementById('uI').addEventListener('keydown',e=>{if(e.key==='Enter')addL()});

// Stats
async function refStats(){
  try{
    const r=await fetch('/api/stats?_='+Date.now());if(!r.ok)return;const d=await r.json();
    const tot=d.total||0,suc=d.success||0,err=d.errors||0,tl=d.total_links||0,run=d.running||false,res=d.results||[];
    document.getElementById('vT').textContent=tot;
    document.getElementById('vS').textContent=suc;
    document.getElementById('vE').textContent=err;
    document.getElementById('vR').textContent=tot?Math.round(suc/tot*100)+'%':'--';
    document.getElementById('pF').style.width=(tl?tot/tl*100:0)+'%';
    document.getElementById('pL').textContent=tot+' / '+tl;
    // Status dot — check control state too
    const cr=await fetch('/api/control');const cd=await cr.json();
    const dot=document.getElementById('dot'),lbl=document.getElementById('stLbl');
    window.nextRoundAt = d.next_round_at || 0;
    if(cd.stopped){dot.className='dot stopped';lbl.textContent='Stopped'}
    else if(cd.paused){dot.className='dot paused';lbl.textContent='Paused'}
    else if(run){dot.className='dot run';lbl.textContent='Running'}
    else if(tot){
      const remaining = Math.max(0, Math.round(window.nextRoundAt - Date.now()/1000));
      dot.className='dot done';
      lbl.textContent = remaining > 0 ? `Sleeping (Next round in ${remaining}s)` : 'Sleeping (Next round soon)';
    }
    else{dot.className='dot idle';lbl.textContent='Idle'}
    const tb=document.getElementById('rB');
    if(!res.length){tb.innerHTML='<tr><td colspan="5" class="empty">No results yet</td></tr>';return}
    tb.innerHTML=res.map((r,i)=>{
      const c=r.status==='success'?'t-ok':(r.status==='running'?'t-run':'t-err');
      const t=r.status==='success'?'OK':(r.status==='running'?'Running':'Error');
      return`<tr><td>${i+1}</td><td class="mono" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${r.url||''}">${r.url||'--'}</td><td class="mono" style="color:var(--accent)">${r.email||'--'}</td><td><span class="tag ${c}">${t}</span></td><td class="mono">${r.timestamp||'--'}</td></tr>`;
    }).join('');
  }catch{}
}

// Logs
async function refLogs(){
  try{
    const r=await fetch('/api/logs?_='+Date.now());if(!r.ok)return;const d=await r.json();
    const logs=d.logs||[];
    document.getElementById('lgC').textContent=logs.length+' entries';
    const v=document.getElementById('lgV');
    if(!logs.length){v.innerHTML='<div class="log-l" style="color:var(--muted)">Waiting for automation...</div>';return}
    const atBottom=v.scrollHeight-v.scrollTop-v.clientHeight<50;
    const last80=logs.slice(-80);
    v.innerHTML=last80.map(l=>`<div class="log-l"><span class="ts">${l.time||''}</span> <span class="${l.level||'INFO'}">[${l.level||'INFO'}]</span> ${(l.message||'').replace(/</g,'&lt;')}</div>`).join('');
    if(atBottom)v.scrollTop=v.scrollHeight;
  }catch{}
}

function tickCountdown(){
  const dot=document.getElementById('dot'),lbl=document.getElementById('stLbl');
  if(dot.classList.contains('done') && window.nextRoundAt > 0){
    const remaining = Math.max(0, Math.round(window.nextRoundAt - Date.now()/1000));
    lbl.textContent = remaining > 0 ? `Sleeping (Next round in ${remaining}s)` : 'Sleeping (Next round soon)';
  }
}

async function ref(){const ls=await getL();drawL(ls);await refStats();await refLogs()}
ref();
setInterval(ref,3000);
setInterval(tickCountdown,1000);
</script>
</body>
</html>
"""


def read_links():
    if not os.path.exists(LINKS_FILE): return []
    with open(LINKS_FILE, 'r') as f:
        return [l.strip() for l in f if l.strip() and l.strip().startswith('http')]

def write_links(links):
    with open(LINKS_FILE, 'w') as f:
        f.write('\n'.join(links) + '\n' if links else '')

def read_control():
    try:
        if os.path.exists(CONTROL_FILE):
            with open(CONTROL_FILE, 'r') as f: return json.load(f)
    except: pass
    return dict(DEFAULT_CONTROL)

def write_control(data):
    current = read_control()
    current.update(data)
    with open(CONTROL_FILE, 'w') as f: json.dump(current, f, indent=2)
    return current


IN_MEMORY_LOGS = []


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._html(DASHBOARD_HTML)
        elif self.path.startswith('/api/stats'):
            self._file(STATS_FILE, {"total":0,"success":0,"errors":0,"total_links":0,"running":False,"results":[]})
        elif self.path == '/api/links':
            self._json({"links": read_links()})
        elif self.path.startswith('/api/logs'):
            self._json({"logs": IN_MEMORY_LOGS})
        elif self.path.startswith('/api/control'):
            self._json(read_control())
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == '/api/links':
            d = self._body()
            url = d.get('url', '').strip()
            if not url or not url.startswith('http'):
                self._json({"success":False,"error":"Invalid URL"}); return
            ls = read_links()
            if url in ls:
                self._json({"success":False,"error":"Already exists"}); return
            ls.append(url); write_links(ls)
            self._json({"success":True,"links":ls})
        elif self.path == '/api/control':
            d = self._body()
            updated = write_control(d)
            self._json({"success":True, **updated})
        elif self.path == '/api/logs':
            d = self._body()
            if isinstance(d, dict) and 'message' in d:
                IN_MEMORY_LOGS.append(d)
                if len(IN_MEMORY_LOGS) > 200:
                    IN_MEMORY_LOGS.pop(0)
            self._json({"success":True})
        elif self.path == '/api/telegram/test':
            d = self._body()
            token = d.get('telegram_token', '').strip()
            chat_id = d.get('telegram_chat_id', '').strip()
            if not token or not chat_id:
                self._json({"success": False, "error": "Token and Chat ID are required."})
                return
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                r = requests.post(url, json={
                    "chat_id": chat_id,
                    "text": "🔔 *TeraBox Automator: Test connection successful!* Your Telegram Bot is configured correctly.",
                    "parse_mode": "Markdown"
                }, timeout=10)
                if r.status_code == 200:
                    resp_json = r.json()
                    if resp_json.get("ok"):
                        self._json({"success": True})
                    else:
                        self._json({"success": False, "error": resp_json.get("description", "Unknown Telegram error")})
                else:
                    self._json({"success": False, "error": f"Telegram API returned status {r.status_code}"})
            except Exception as e:
                self._json({"success": False, "error": str(e)})
        else: self.send_response(404); self.end_headers()

    def do_DELETE(self):
        if self.path == '/api/links':
            d = self._body(); ls = read_links()
            if d.get('clear_all'): ls = []
            elif 'index' in d:
                i = int(d['index'])
                if 0 <= i < len(ls): ls.pop(i)
            write_links(ls)
            self._json({"success":True,"links":ls})
        else: self.send_response(404); self.end_headers()

    def _body(self):
        return json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))).decode())

    def _html(self, c):
        self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers()
        self.wfile.write(c.encode('utf-8'))

    def _json(self, d):
        self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-cache'); self.end_headers()
        self.wfile.write(json.dumps(d).encode('utf-8'))

    def _file(self, path, default):
        try:
            if os.path.exists(path):
                with open(path,'r') as f: self._json(json.load(f))
            else: self._json(default)
        except: self._json(default)

    def log_message(self, *a): pass


def telegram_bot_loop():
    print("[Telegram Bot] Background monitoring thread started.")
    last_token = None
    last_update_id = 0
    
    while True:
        try:
            # Load config from control.json or env vars
            c = read_control()
            token = c.get("telegram_token", "").strip() or os.environ.get("TELEGRAM_TOKEN", "").strip()
            chat_id = c.get("telegram_chat_id", "").strip() or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
            
            if not token:
                last_token = None
                time.sleep(5)
                continue
                
            # If the token changed, reset the update ID
            if token != last_token:
                print(f"[Telegram Bot] Token initialized/changed. Starting listener...")
                last_token = token
                last_update_id = 0
                
            # Poll updates
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=10"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        last_update_id = update.get("update_id")
                        message = update.get("message")
                        if not message:
                            continue
                            
                        msg_chat_id = message.get("chat", {}).get("id")
                        
                        # Security Check
                        if chat_id and str(msg_chat_id) != str(chat_id):
                            continue
                            
                        text = message.get("text", "").strip()
                        if not text:
                            continue
                            
                        # Commands
                        if text.startswith("/stats") or text.startswith("/status"):
                            stats = {"total": 0, "success": 0, "errors": 0, "running": False}
                            try:
                                if os.path.exists(STATS_FILE):
                                    with open(STATS_FILE, 'r') as f:
                                        stats = json.load(f)
                            except:
                                pass
                                
                            c_state = read_control()
                            status_str = "Running"
                            if c_state.get("stopped"):
                                status_str = "Stopped"
                            elif c_state.get("paused"):
                                status_str = "Paused"
                            elif not stats.get("running"):
                                status_str = "Sleeping (Between rounds)"
                                
                            tot = stats.get("total", 0)
                            suc = stats.get("success", 0)
                            err = stats.get("errors", 0)
                            rate = f"{round(suc/tot*100)}%" if tot > 0 else "0%"
                            
                            reply = (
                                f"📊 *TeraBox Referral Automator Stats*\n\n"
                                f"⚫ *Status:* {status_str}\n"
                                f"🔄 *Processed:* {tot}\n"
                                f"✅ *Success:* {suc}\n"
                                f"❌ *Errors:* {err}\n"
                                f"📈 *Success Rate:* {rate}"
                            )
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                "chat_id": msg_chat_id,
                                "text": reply,
                                "parse_mode": "Markdown"
                            })
                            
                        elif text.startswith("/pause"):
                            write_control({"paused": True})
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                "chat_id": msg_chat_id,
                                "text": "⏸️ *Automation paused via Telegram.*",
                                "parse_mode": "Markdown"
                            })
                            
                        elif text.startswith("/resume"):
                            write_control({"paused": False, "stopped": False})
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                "chat_id": msg_chat_id,
                                "text": "▶️ *Automation resumed via Telegram.*",
                                "parse_mode": "Markdown"
                            })
                            
                        elif text.startswith("/stop"):
                            write_control({"stopped": True})
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                "chat_id": msg_chat_id,
                                "text": "🛑 *Automation stopped/killed via Telegram.*",
                                "parse_mode": "Markdown"
                            })
                            
                        elif text.startswith("/addlink "):
                            link = text.replace("/addlink ", "").strip()
                            if not link.startswith("http"):
                                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                    "chat_id": msg_chat_id,
                                    "text": "❌ *Invalid URL. Must start with http.*",
                                    "parse_mode": "Markdown"
                                })
                            else:
                                ls = read_links()
                                if link in ls:
                                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                        "chat_id": msg_chat_id,
                                        "text": "⚠️ *URL already exists in link list.*",
                                        "parse_mode": "Markdown"
                                    })
                                else:
                                    ls.append(link)
                                    write_links(ls)
                                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                        "chat_id": msg_chat_id,
                                        "text": f"✅ *Link added:* `{link}`",
                                        "parse_mode": "Markdown"
                                    })
                                    
                        elif text.startswith("/help") or text.startswith("/start"):
                            reply = (
                                f"🤖 *TeraBox Automator Bot Commands*\n\n"
                                f"/stats \- Get current stats\n"
                                f"/pause \- Pause automation\n"
                                f"/resume \- Resume automation\n"
                                f"/stop \- Stop automation\n"
                                f"/addlink `<url>` \- Add a referral link"
                            )
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                                "chat_id": msg_chat_id,
                                "text": reply,
                                "parse_mode": "MarkdownV2"
                            })
            elif r.status_code == 401:
                last_token = None
                time.sleep(10)
            else:
                time.sleep(5)
        except Exception as e:
            time.sleep(5)


if __name__ == '__main__':
    # Initialize control file with defaults
    if not os.path.exists(CONTROL_FILE):
        write_control(DEFAULT_CONTROL)
        
    # Start Telegram status bot thread in background
    t = threading.Thread(target=telegram_bot_loop, daemon=True)
    t.start()
        
    with socketserver.TCPServer(("", PORT), Handler) as h:
        print(f"\n  TeraBox Dashboard: http://localhost:{PORT}\n")
        try: h.serve_forever()
        except KeyboardInterrupt: print("\n  Stopped.")

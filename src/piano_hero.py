#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time, threading, json
from flask import Flask, jsonify, Response, request
import RPi.GPIO as GPIO

# ================== Hardware ==================
COMMON_ANODE = True
PIN_R, PIN_G, PIN_B = 17, 27, 22
PIN_SPK = 18   # 2N3904: GPIO18->1k (Basis), 5V->330Ω->+Speaker

GPIO.setmode(GPIO.BCM); GPIO.setwarnings(False)
for p in (PIN_R,PIN_G,PIN_B,PIN_SPK): GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)

pwm_r = GPIO.PWM(PIN_R, 1000); pwm_g = GPIO.PWM(PIN_G, 1000); pwm_b = GPIO.PWM(PIN_B, 1000)
for pwm in (pwm_r,pwm_g,pwm_b): pwm.start(100 if COMMON_ANODE else 0)
spk_pwm = GPIO.PWM(PIN_SPK, 440); spk_pwm.start(0)

LED_GAIN = {"R":50,"G":80,"B":90}
COLOR_FOR = {"a":("R",100),"s":("R",70),"d":("G",100),"f":("G",80),
             "j":("B",90),"k":("B",80),"l":("R",85),"ö":("G",90),";":("G",90),"[":("G",90)}

def _apply(ch,pct):
    pct=max(0,min(100,int(pct)))
    if COMMON_ANODE: pct=100-pct
    {"R":pwm_r,"G":pwm_g,"B":pwm_b}[ch].ChangeDutyCycle(pct)

def led_off():
    for ch in ("R","G","B"): _apply(ch,0)

def led_for_key(k, ms=120):
    ch, base = COLOR_FOR.get(k, ("G",70))
    lvl = int(base*LED_GAIN[ch]/100)
    _apply(ch,lvl); time.sleep(ms/1000); led_off()

# ======= Audio (sanfte Hüllkurve) =======
ENABLE_TONE = True
def tone_env(freq, ms, duty=33):
    if not ENABLE_TONE: time.sleep(ms/1000); return
    spk_pwm.ChangeFrequency(int(freq))
    total = max(80, int(ms))
    a = max(8, int(0.06*total)); r = max(8, int(0.08*total)); s = max(0, total - a - r)
    # Attack
    for dc in (int(duty*0.5), int(duty*0.8), duty):
        spk_pwm.ChangeDutyCycle(dc); time.sleep(a/3/1000)
    # Sustain
    spk_pwm.ChangeDutyCycle(duty); time.sleep(s/1000)
    # Release
    for dc in (int(duty*0.8), int(duty*0.4), 0):
        spk_pwm.ChangeDutyCycle(dc); time.sleep(r/3/1000)
    spk_pwm.ChangeDutyCycle(0)

def beep_led(k, ms=120):
    threading.Thread(target=lambda: led_for_key(k, ms), daemon=True).start()

def jingle_fail():
    for _ in range(2):
        _apply("R", LED_GAIN["R"]); time.sleep(0.08); led_off(); time.sleep(0.05)
    for f in [440,392,349,329,293,262]: tone_env(f,110); time.sleep(0.005)

def fx_success():
    for _ in range(3):
        _apply("G", LED_GAIN["G"]); time.sleep(0.07); led_off(); time.sleep(0.05)

# ======= Frequenzen =======
N = {
    "B0":31,"C1":33,"CS1":35,"D1":37,"DS1":39,"E1":41,"F1":44,"FS1":46,"G1":49,"GS1":52,"A1":55,"AS1":58,
    "B1":62,"C2":65,"CS2":69,"D2":73,"DS2":78,"E2":82,"F2":87,"FS2":93,"G2":98,"GS2":104,"A2":110,"AS2":117,
    "B2":123,"C3":131,"CS3":139,"D3":147,"DS3":156,"E3":165,"F3":175,"FS3":185,"G3":196,"GS3":208,"A3":220,"AS3":233,
    "B3":247,"C4":262,"CS4":277,"D4":294,"DS4":311,"E4":330,"F4":349,"FS4":370,"G4":392,"GS4":415,"A4":440,"AS4":466,
    "B4":494,"C5":523,"CS5":554,"D5":587,"DS5":622,"E5":659,"F5":698,"FS5":740,"G5":784,"GS5":830,"A5":880,"AS5":932,
    "B5":988,"C6":1047
}

# ======= 3 Melodien =======
MARIO = {
    "name":"Mario – Overworld (Intro)",
    "bpm": 150,
    "seq":[
        ("E5",0.5),("E5",0.5),("R",0.5),("E5",0.5),
        ("R",0.5),("C5",0.5),("E5",0.5),("R",0.5),("G5",1.0),
        ("R",1.0),
        ("G4",0.5),("R",0.5),("C5",0.5),("R",0.5),("G4",0.5),("R",0.5),("E4",0.5),("R",0.5),
        ("A4",0.5),("R",0.5),("B4",0.5),("R",0.5),("AS4",0.5),("A4",0.5),
        ("R",0.5),("G4",0.5),("E5",0.5),("G5",0.5),("A5",0.5),("R",0.5),
        ("F5",0.5),("G5",0.5),("R",0.5),("E5",0.5),("R",0.5),("C5",0.5),("D5",0.5),("B4",1.0)
    ]
}
HAPPY = {
    "name":"Happy Birthday",
    "bpm": 120,
    "seq":[
        ("G4",1),("G4",0.5),("A4",1),("G4",1),("C5",1),("B4",2),
        ("G4",1),("G4",0.5),("A4",1),("G4",1),("D5",1),("C5",2),
        ("G4",1),("G4",0.5),("G5",1),("E5",1),("C5",1),("B4",1),("A4",2),
        ("F5",1),("F5",0.5),("E5",1),("C5",1),("D5",1),("C5",2)
    ]
}
ODE = {
    "name":"Ode to Joy",
    "bpm": 110,
    "seq":[
        ("E4",1),("E4",1),("F4",1),("G4",1),("G4",1),("F4",1),("E4",1),("D4",1),
        ("C4",1),("C4",1),("D4",1),("E4",1),("E4",1.5),("D4",0.5),("D4",2),
        ("E4",1),("E4",1),("F4",1),("G4",1),("G4",1),("F4",1),("E4",1),("D4",1),
        ("C4",1),("C4",1),("D4",1),("E4",1),("D4",1.5),("C4",0.5),("C4",2)
    ]
}
MELODIES = {"mario":MARIO, "happy":HAPPY, "ode":ODE}

# ----- Noten -> Lane (a s d f | j k l ö) -----
LANES = ["a","s","d","f","j","k","l","ö"]
PITCH_MIN, PITCH_MAX = N["C4"], N["C6"]  # 262..1047
def lane_for_hz(hz:int)->str:
    hz_clamped = max(PITCH_MIN, min(PITCH_MAX, hz))
    idx = int((hz_clamped - PITCH_MIN) / (PITCH_MAX-PITCH_MIN+1e-9) * len(LANES))
    idx = min(len(LANES)-1, idx)
    return LANES[idx]

def seq_to_chart(seq, bpm, leadin_beats=2.0):
    ms_per_beat = 60000.0/bpm
    t = leadin_beats*ms_per_beat
    notes=[]
    for name, beats in seq:
        dur = max(0.25, beats)*ms_per_beat
        if name=="R":
            t += dur; continue
        hz = N[name]
        k  = lane_for_hz(hz)
        notes.append({"k":k, "t_ms":int(t), "dur_ms":int(dur), "hz":int(hz)})
        t += dur
    return notes, int(ms_per_beat)

def play_note(hz:int, dur_ms:int, lane_key:str=None):
    if lane_key: beep_led(lane_key, dur_ms)
    tone_env(hz, dur_ms)

def autoplay_melody(name:str, bpm:int):
    m = MELODIES[name]
    ms_per_beat = 60000.0/bpm
    for n,beats in m["seq"]:
        if n=="R":
            time.sleep(max(0.25,beats)*ms_per_beat/1000.0); continue
        dur = int(max(0.25,beats)*ms_per_beat)
        k = lane_for_hz(N[n])
        play_note(N[n], dur, k)
        time.sleep(0.02)

def playback_events(events):
    if not events: return
    t0 = events[0]["dt"]
    for i,ev in enumerate(events):
        wait = max(0, (ev["dt"] - (events[i-1]["dt"] if i else t0)))/1000.0
        time.sleep(wait)
        dur = max(100, int(0.5*((events[i+1]["dt"]-ev["dt"]) if i<len(events)-1 else 180)))
        tone_env(ev["hz"], dur)

# ================== Flask App ==================
app = Flask(__name__)

HTML = """
<!doctype html><html><head><meta charset="utf-8"><title>Piano-Hero++</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  :root{--bg:#0b0c10;--panel:#111;--lane:#0f1116;--grid1:#1d2027;--grid2:#2b303a}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:#eee;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial}
  .top{display:flex;align-items:center;gap:.75rem;padding:12px 16px;background:var(--panel);flex-wrap:wrap}
  select,.btn,input[type=range]{background:#222;color:#eee;border:1px solid #444;border-radius:8px;padding:8px 10px}
  input[type=range]{padding:6px}
  .btn{cursor:pointer}
  .stat{margin-left:auto}
  .wrap{position:relative;height:74vh}
  #game{display:block;width:100%;height:100%;background:#14161a;border-top:1px solid #222;border-bottom:1px solid #222}
  .hud{display:flex;gap:12px;padding:8px 16px;background:var(--panel);border-top:1px solid #222}
  .badge{background:#1c1f25;border:1px solid #2a2f38;border-radius:8px;padding:6px 10px}
  .hit{color:#9cff8b}.good{color:#ffe07a}.miss{color:#ff8b8b}
  .met{width:10px;height:10px;border-radius:50%;background:#333;display:inline-block;margin-left:8px}
  .met.on{background:#fff}
  .countdown{position:absolute;inset:0;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.45);font-size:72px;font-weight:800}
  .countdown.show{display:flex}
  .small{color:#bbb}
</style></head><body>
<div class="top">
  <label>Melodie:
    <select id="mel">
      <option value="mario">Mario – Overworld</option>
      <option value="happy">Happy Birthday</option>
      <option value="ode">Ode to Joy</option>
    </select>
  </label>

  <label>BPM:
    <input id="bpm" type="range" min="60" max="200" value="140" oninput="bpmLabel.innerText=this.value"/>
    <b id="bpmLabel">140</b>
  </label>

  <label>Timing:
    <input id="win" type="range" min="150" max="400" step="10" value="240"
           oninput="winLabel.innerText=this.value;updateHitWindowFromUI()"/>
    <b id="winLabel">240</b> ms
  </label>

  <span class="small">Tasten: <b>a s d f | j k l ö</b></span>
  <button class="btn" id="preview">Vorschau</button>
  <button class="btn" id="start">Start</button>

  <span class="stat small">Score: <b id="score">0</b> • Combo: <b id="combo">0</b> • Acc: <b id="acc">100%</b></span>
</div>

<div class="wrap">
  <canvas id="game"></canvas>
  <div id="cd" class="countdown"></div>
</div>

<div class="hud">
  <span id="last" class="badge">Ready</span>
  <span id="hw" class="badge small"></span>
  <span style="margin-left:auto">Tempo: <b id="tempoView">–</b> BPM <span id="met" class="met"></span></span>
</div>

<script>
const lanes = ['a','s','d','f','j','k','l','ö']; // 8 Lanes
const fallMsDefault = 1800;
let chart=[], bpm=140, msPerBeat=500, travelMs=fallMsDefault, startAt=0, hitlineY=0;
let score=0, combo=0, total=0, hits=0, running=false, isCounting=false, lastMsg='Ready', lastHitClass='';
let performed=[]; // {k,dt,hz}
let hitWinGood = 240;             // ms – per Slider verstellbar
let hitWinPerfect = hitWinGood/2; // Perfect = Hälfte

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d',{alpha:false});
let W=0,H=0,laneW=0;

function resize(){
  const r = canvas.parentElement.getBoundingClientRect();
  canvas.width = Math.floor(r.width);
  canvas.height= Math.floor(r.height);
  W=canvas.width; H=canvas.height; laneW=W/lanes.length; hitlineY=H*0.9;
}
window.addEventListener('resize', resize);

// --- UI Lock während Countdown ---
function lockUI(lock){
  ['mel','bpm','win','preview'].forEach(id=>{
    const el=document.getElementById(id);
    if(!el) return;
    el.disabled = lock;
    el.style.opacity = lock ? 0.5 : 1;
    el.style.pointerEvents = lock ? 'none' : 'auto';
  });
}

function drawFrame(now){
  ctx.fillStyle='#14161a'; ctx.fillRect(0,0,W,H);
  for(let i=0;i<lanes.length;i++){
    ctx.fillStyle = '#0f1116'; ctx.fillRect(i*laneW,0,laneW,H);
    ctx.fillStyle='#1d2027'; ctx.fillRect(i*laneW,0,2,H);
    ctx.fillStyle='#2b303a'; ctx.fillRect((i+1)*laneW-2,0,2,H);
    ctx.fillStyle='#8892a6'; ctx.fillText(lanes[i], i*laneW+laneW/2-3, 18);
  }
  ctx.strokeStyle='#999'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(0,hitlineY); ctx.lineTo(W,hitlineY); ctx.stroke();

  if(msPerBeat>0){
    const phase=((now-startAt)%msPerBeat)/msPerBeat;
    document.getElementById('met').className='met'+(phase<0.5?' on':'');
  }

  chart.forEach(n=>{
    if(n.judged) return;
    const y=(now-(startAt+n.t_ms-travelMs))*(H/travelMs);
    if (y>-40 && y<H+40){
      const x=lanes.indexOf(n.k)*laneW;
      ctx.fillStyle='#3da5ff'; ctx.fillRect(x+10,y-18,laneW-20,16);
    }
  });

  requestAnimationFrame(drawFrame);
}

function updateHitWindowFromUI(){
  hitWinGood = parseInt(document.getElementById('win').value,10);
  hitWinPerfect = Math.round(hitWinGood/2);
  document.getElementById('hw').innerText =
    `Perfect ≤ ${hitWinPerfect}ms • Good ≤ ${hitWinGood}ms • Miss > ${hitWinGood}ms`;
}

function loadChart(){
  running = FalseIfCounting(); isCounting=false; lockUI(false);
  const name=document.getElementById('mel').value;
  bpm = parseInt(document.getElementById('bpm').value,10);
  fetch('/chart/'+name+'?bpm='+bpm).then(r=>r.json()).then(j=>{
    chart=j.notes.map(n=>({...n}));
    msPerBeat=j.ms_per_beat; travelMs=j.travel_ms;
    startAt=performance.now()+800; // für Metronom
    score=0; combo=0; hits=0; total=chart.length; performed=[];
    document.getElementById('tempoView').innerText=bpm;
    setMsg(total? 'Ready' : 'Keine Noten',''); updateHUD();
  });
}
function FalseIfCounting(){ return false; } // Klarer Reset-Helfer

function doCountdown(cb){
  const cd=document.getElementById('cd'); let n=3;
  cd.className='countdown show'; cd.innerText=n;
  const t=setInterval(()=>{
    n--; if(n===0){ cd.innerText='GO!'; clearInterval(t); setTimeout(()=>{ cd.className='countdown'; cb(); },500); }
    else cd.innerText=n;
  }, 700);
}

function startRun(){
  running = true;
  performed.length = 0;
  startAt = performance.now() + 800; // genügend Vorlauf nach GO
  setMsg('Go!','');
}

function preview(){
  const name=document.getElementById('mel').value;
  const bpm=parseInt(document.getElementById('bpm').value,10);
  fetch('/preview?m='+name+'&bpm='+bpm);
}

function beep(hz,dur){ fetch('/beep?hz='+hz+'&dur='+Math.max(80,Math.floor(dur))); }

function judge(k, when){
  if(!running){ setMsg('Drücke Start',''); return; }
  let candidate=null,bestDt=1e9;
  for(const n of chart){
    if(n.k!==k || n.judged) continue;
    const dt=Math.abs((startAt+n.t_ms)-when);
    if(dt<bestDt){ bestDt=dt; candidate=n; }
    if((startAt+n.t_ms)>when+Math.max(200,hitWinGood)) break;
  }
  if(!candidate){ setMsg('Miss','miss'); combo=0; updateHUD(); return; }

  const dt=bestDt;
  if(dt<=hitWinPerfect){ score+=300; combo++; hits++; candidate.judged=true; setMsg('Perfect','hit'); beep(candidate.hz,candidate.dur_ms*0.9); }
  else if(dt<=hitWinGood){ score+=100; combo++; hits++; candidate.judged=true; setMsg('Good','good'); beep(candidate.hz,candidate.dur_ms*0.75); }
  else { combo=0; setMsg('Miss','miss'); }

  // Auto-Miss nach gewählter Good-Toleranz
  chart.forEach(n=>{ if(!n.judged && performance.now()>startAt+n.t_ms+hitWinGood){ n.judged=true; combo=0; } });

  // Runde fertig?
  if(chart.every(n=>n.judged)){
    running=false;
    if(hits/total>=0.6){
      setMsg('SUCCESS – Playback deiner Version…','hit');
      fetch('/autoplay?m='+document.getElementById('mel').value+'&bpm='+bpm);
      fetch('/playback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({events:performed})});
    }else{
      setMsg('Fehler – erneut versuchen','miss'); fetch('/fail');
    }
  }
  updateHUD();
}

function updateHUD(){
  const acc = total? Math.round(100*hits/total):100;
  document.getElementById('score').innerText=score;
  document.getElementById('combo').innerText=combo;
  document.getElementById('acc').innerText=acc+'%';
}
function setMsg(msg, cls){ const el=document.getElementById('last'); el.innerText=msg; el.className='badge '+cls; }

// Tastatur inkl. ö-Fallbacks
const down={}; function normKey(k){k=k.toLowerCase(); if(k===';'||k==='[') return 'ö'; return k;}
document.addEventListener('keydown', e=>{
  let k=normKey(e.key); if(!lanes.includes(k)) return;
  if(!down[k]){
    down[k]=true;
    const now=performance.now();
    // nächste Note der Lane (für Playback)
    let cand=null;
    for(const n of chart){ if(n.k===k && !n.judged){ cand=n; break; } }
    if(cand) performed.push({k, dt: Math.round(now - startAt), hz: cand.hz});
    judge(k, now);
  }
});
document.addEventListener('keyup', e=>{ down[normKey(e.key)]=false; });

document.getElementById('mel').addEventListener('change', loadChart);
document.getElementById('bpm').addEventListener('change', loadChart);
document.getElementById('preview').addEventListener('click', preview);

document.getElementById('start').addEventListener('click', ()=>{
  if (!chart || chart.length === 0){ setMsg('Kein Chart geladen','miss'); return; }
  if (running || isCounting) return; // Doppelstart blocken
  isCounting = TrueIfLock();          // UI sperren
  doCountdown(()=>{
    startRun();
    isCounting = false;
    lockUI(false);
  });
});

function TrueIfLock(){ lockUI(true); return true; }

resize(); requestAnimationFrame(drawFrame); updateHitWindowFromUI(); loadChart();
</script>
</body></html>
"""

app = Flask(__name__)

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")

@app.route("/chart/<name>")
def chart(name):
    if name not in MELODIES: name="mario"
    bpm = int(request.args.get("bpm", MELODIES[name]["bpm"]))
    notes, ms_per_beat = seq_to_chart(MELODIES[name]["seq"], bpm, leadin_beats=2.0)
    return jsonify({"bpm": bpm, "ms_per_beat": ms_per_beat, "travel_ms": 1800, "notes": notes})

@app.route("/beep")
def beep_route():
    try:
        hz = int(float(request.args.get("hz","0")))
        dur= int(float(request.args.get("dur","120")))
        if hz>0: tone_env(hz, dur)
    except: pass
    return ("",204)

@app.route("/preview")
def preview_route():
    name = request.args.get("m","mario")
    bpm  = int(request.args.get("bpm", MELODIES.get(name, MARIO)["bpm"]))
    if name not in MELODIES: name="mario"
    threading.Thread(target=lambda: autoplay_melody(name, bpm), daemon=True).start()
    return ("",204)

@app.route("/autoplay")
def route_autoplay():
    name = request.args.get("m","mario")
    bpm  = int(request.args.get("bpm", MELODIES.get(name, MARIO)["bpm"]))
    if name not in MELODIES: name="mario"
    def job(): fx_success(); autoplay_melody(name, bpm)
    threading.Thread(target=job, daemon=True).start()
    return ("",204)

@app.route("/fail")
def route_fail():
    threading.Thread(target=jingle_fail, daemon=True).start()
    return ("",204)

@app.route("/playback", methods=["POST"])
def route_playback():
    try:
        data = request.get_json(force=True) or {}
        events = [e for e in data.get("events", []) if isinstance(e, dict) and isinstance(e.get("hz",None),(int,float)) and isinstance(e.get("dt",None),(int,float))]
        threading.Thread(target=lambda: playback_events(events), daemon=True).start()
    except Exception:
        pass
    return ("",204)

def cleanup():
    try:
        led_off()
        for pwm in (pwm_r,pwm_g,pwm_b,spk_pwm): pwm.stop()
        GPIO.cleanup()
    except: pass

if __name__ == "__main__":
    try:
        print("Piano-Hero++ läuft auf http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000)
    finally:
        cleanup()

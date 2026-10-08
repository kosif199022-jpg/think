"""Browser-only Three.js 3D animation adapter for the KOSIF graphics lane.

Requires Internet and WebGL in the viewer browser; no Blender or paid API.
The output is an interactive HTML preview, not an MP4 video.
"""
import html
import json


def build_space_scene(title="KOSIF Space", duration_seconds=5, width=960, height=540):
    duration = float(duration_seconds)
    if not 0.5 <= duration <= 30:
        raise ValueError("duration_seconds must be within 0.5..30")
    width, height = int(width), int(height)
    if not (240 <= width <= 3840 and 240 <= height <= 2160):
        raise ValueError("invalid scene dimensions")
    config = json.dumps({"duration": duration, "width": width, "height": height})
    return _PAGE.replace("__CONFIG__", config).replace(
        "__TITLE__", html.escape(str(title)[:100], quote=True)
    )


_PAGE = """<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
body{margin:0;background:#070e1f;color:#eef5ff;font:16px system-ui;padding:14px}
main{max-width:960px;margin:auto}h1{font-size:22px}
#stage{position:relative;min-height:200px;overflow:hidden;border:1px solid #314162;
border-radius:14px;background:radial-gradient(#182c58,#040712 75%)}
#stage canvas{display:block}#hint{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:16px}#hint[hidden]{display:none}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:12px}
button{min-height:44px;padding:8px 20px;border-radius:9px;background:#224675;color:white;border:1px solid #698dbb;font:inherit}
button:disabled{opacity:.4}progress{flex:1;min-width:100px}
#status{color:#b7c9e4;font-size:13px}
</style></head><body><main>
<h1>__TITLE__</h1><div id="stage" aria-label="مشهد كوكب ومركبة في الفضاء ثلاثي الأبعاد">
<div id="hint">جار تحميل Three.js...</div></div>
<div class="controls"><button id="play" type="button" disabled>تشغيل</button>
<button id="replay" type="button" disabled>إعادة</button>
<progress id="bar" max="100" value="0"></progress>
<span id="clock"></span></div><p id="status" role="status"></p>
</main><script type="module">
const cfg=__CONFIG__, stage=document.getElementById("stage"), hint=document.getElementById("hint"),
play=document.getElementById("play"), replay=document.getElementById("replay"),
bar=document.getElementById("bar"), clock=document.getElementById("clock"),
status=document.getElementById("status");
stage.style.aspectRatio=cfg.width+"/"+cfg.height;
clock.textContent="0.0 / "+cfg.duration.toFixed(1)+" ث";
try{
const THREE=await import("https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js");
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:"low-power"});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
renderer.outputColorSpace=THREE.SRGBColorSpace;
stage.appendChild(renderer.domElement);hint.hidden=true;
const world=new THREE.Scene();world.background=new THREE.Color(0x050917);
const camera=new THREE.PerspectiveCamera(48,1,.1,200);camera.position.set(0,3,19);
world.add(new THREE.AmbientLight(0x91a8d1,1.1));
const key=new THREE.PointLight(0xffe2c2,90,80);key.position.set(-9,5,10);world.add(key);
const planet=new THREE.Mesh(new THREE.SphereGeometry(4,48,36),
new THREE.MeshStandardMaterial({color:0x5c8da9,metalness:.2,roughness:.7}));
world.add(planet);
const ring=new THREE.Mesh(new THREE.TorusGeometry(6.2,.58,12,120),
new THREE.MeshStandardMaterial({color:0xc1ab87,side:THREE.DoubleSide}));
ring.rotation.set(1.12,.14,0);world.add(ring);
const moon=new THREE.Mesh(new THREE.SphereGeometry(.7,20,16),
new THREE.MeshStandardMaterial({color:0xb6a6b1}));world.add(moon);
const ship=new THREE.Group();
const hull=new THREE.Mesh(new THREE.ConeGeometry(.35,1.55,10),
new THREE.MeshStandardMaterial({color:0xe7f8ff,metalness:.5,roughness:.35}));
hull.rotation.z=-Math.PI/2;ship.add(hull);
const light=new THREE.PointLight(0x38bdf8,2,4);light.position.set(-.8,0,0);ship.add(light);
world.add(ship);
let seed=1187;function rand(){seed=(1664525*seed+1013904223)>>>0;return seed/4294967296}
const xyz=new Float32Array(1000*3);
for(let i=0;i<xyz.length;i+=3){
xyz[i]=(rand()-.5)*145;xyz[i+1]=(rand()-.5)*90;xyz[i+2]=-20-rand()*80}
const geo=new THREE.BufferGeometry();
geo.setAttribute("position",new THREE.BufferAttribute(xyz,3));
const stars=new THREE.Points(geo,new THREE.PointsMaterial({color:0xe0f3ff,size:.17}));
world.add(stars);
function resize(){const w=Math.max(stage.clientWidth,1),h=Math.max(stage.clientHeight,1);
renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
resize();window.addEventListener("resize",resize);
if(typeof ResizeObserver!=="undefined")new ResizeObserver(resize).observe(stage);
let elapsed=0,started=0,running=false,frameId=0;
function draw(t){const pct=t/cfg.duration;
planet.rotation.y=t*.25;ring.rotation.z=.05*Math.sin(t);
moon.position.set(9*Math.cos(t*.2),1.6*Math.sin(t*.32),-4);
ship.position.set(-10+20*pct,2+.35*Math.sin(t*3),5);
camera.position.set(Math.sin(t*.3)*1.7,3+.4*Math.sin(t*.5),19-2*pct);
camera.lookAt(0,0,0);stars.rotation.y=t*.005;renderer.render(world,camera);
bar.value=Math.round(pct*100);clock.textContent=t.toFixed(1)+" / "+cfg.duration.toFixed(1)+" ث"}
function stop(){running=false;cancelAnimationFrame(frameId);play.textContent="تشغيل"}
function tick(now){if(!running)return;elapsed=Math.min(cfg.duration,(now-started)/1000);
draw(elapsed);if(elapsed>=cfg.duration){stop();status.textContent="اكتمل المشهد — يمكنك إعادته"}
else frameId=requestAnimationFrame(tick)}
function start(){if(running){stop();status.textContent="إيقاف مؤقت";return}
if(elapsed>=cfg.duration)elapsed=0;started=performance.now()-elapsed*1000;running=true;
play.textContent="إيقاف مؤقت";status.textContent="معاينة Three.js تعمل من المتصفح";
frameId=requestAnimationFrame(tick)}
play.addEventListener("click",start);replay.addEventListener("click",()=>{
stop();elapsed=0;draw(0);start()});
draw(0);play.disabled=false;replay.disabled=false;
if(!window.matchMedia("(prefers-reduced-motion: reduce)").matches)start();
else status.textContent="التشغيل التلقائي معطّل وفق إعداد تقليل الحركة";
}catch(error){hint.textContent="تعذّر تشغيل Three.js. يتطلب إنترنت ومتصفح يدعم WebGL.";
status.textContent=String(error?.message||error)}
</script></body></html>
"""
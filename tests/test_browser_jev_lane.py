import importlib.util, pathlib
P=pathlib.Path(__file__).parents[1]/"src"/"kosif_think"/"browser_jev_lane.py"
spec=importlib.util.spec_from_file_location("lane",P); lane=importlib.util.module_from_spec(spec); spec.loader.exec_module(lane)

def sample(url="https://example.com/login"):
    return {"url":url,"title":"Login","body_text":"Please sign in","dialogs":[],"elements":[
      {"tag":"input","role":"","text":"Email","name":"email","type":"email","aria":"Email","placeholder":"you@example.com","href":"","value":"","checked":None,"disabled":False,"in_viewport":True,"selector":"input[name=\"email\"]","rect":{"x":10,"y":10,"width":200,"height":30}},
      {"tag":"button","role":"button","text":"Continue","name":"","type":"submit","aria":"","placeholder":"","href":"","value":"","checked":None,"disabled":False,"in_viewport":True,"selector":"button:nth-of-type(1)","rect":{"x":10,"y":50,"width":100,"height":30}},
    ]}

g1=lane.build_stable_graph(sample()); g2=lane.build_stable_graph(sample())
assert [n["id"] for n in g1["nodes"]]==[n["id"] for n in g2["nodes"]]
a=lane.assess("enter email address",g1)
assert a["ok"] and a["candidates"] and a["candidates"][0]["node"]["tag"]=="input"
p=lane.decision_packet("click Continue",g1)
assert p["ok"] and set(p["criteria"]).issubset({n["id"] for n in g1["nodes"]})
r=lane._risk(g1["nodes"][1],"CLICK","pay now")
assert r["approval_required"]
g3=lane.build_stable_graph(sample("https://example.com/next"))
old=g1["nodes"][1]; rec=lane.recover(old["id"],g1,g3)
assert rec["ok"] and rec["node"]["text"]=="Continue"
print("browser_jev_lane pure tests: OK")

#!/usr/bin/env python3
import json,sys,os
if len(sys.argv)!=3:
    print("Usage: python3 tools/configure_repo.py GITHUB_USERNAME REPO_NAME")
    raise SystemExit(2)
user,repo=sys.argv[1:3]
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base=f"https://raw.githubusercontent.com/{user}/{repo}/main"
for fn in ("catalog.json","skylink_23.5e.json"):
    p=os.path.join(root,fn)
    data=json.load(open(p,encoding="utf-8"))
    def walk(x):
        if isinstance(x,dict):
            return {k:walk(v) for k,v in x.items()}
        if isinstance(x,list): return [walk(v) for v in x]
        if isinstance(x,str): return x.replace("https://raw.githubusercontent.com/USERNAME/piconhub-server/main",base)
        return x
    data=walk(data)
    json.dump(data,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    open(p,"a").write("\n")
print("Configured base URL:",base)
print("Catalog URL:",base+"/catalog.json")

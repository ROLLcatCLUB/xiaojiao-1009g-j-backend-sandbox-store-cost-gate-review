import argparse, json, re, shutil, subprocess, tempfile, zipfile
from pathlib import Path

SLUG="xiaojiao_backend_sandbox_store_contract_1009G"
FINAL_STATUS="XIAOJIAO_BACKEND_SANDBOX_STORE_CONTRACT_PASS"
MARKER="ALL_1009G_BACKEND_SANDBOX_STORE_CONTRACT_CHECKS_OK"
REQUIRED=[
  "docs/foundation/xiaojiao_backend_sandbox_store_contract_1009G.md",
  "docs/foundation/xiaojiao_backend_sandbox_store_contract_1009G.json",
  "docs/audit/xiaojiao_backend_sandbox_store_contract_1009G_result.json",
  "docs/audit/xiaojiao_backend_sandbox_store_contract_1009G_report.md",
  "docs/audit_packages/xiaojiao_backend_sandbox_store_contract_1009G_manifest.json",
  "docs/audit_packages/xiaojiao_backend_sandbox_store_contract_1009G.zip",
  "scripts/validate_xiaojiao_backend_sandbox_store_contract_1009G.py",
  
  
]
SECRET_PATTERNS=[re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), re.compile(r"gho_[A-Za-z0-9_]{12,}"), re.compile(r"(?i)(authorization|bearer)\s*[:=]\s*['\"]?[^'\"]{12,}")]
FORBIDDEN=[".env","token","secret","api_key","node_modules","__pycache__",".db",".sqlite","dist","build","coverage",".DS_Store"]
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def no_secret(p):
    text=Path(p).read_text(encoding="utf-8", errors="ignore")
    return not any(rx.search(text) for rx in SECRET_PATTERNS)
def check_html(root):
    html=root/"frontend/xiaojiao-preview.html"
    if not html.exists(): return
    text=html.read_text(encoding="utf-8", errors="ignore")
    for marker in ["backend_sandbox","local_fallback","storeModeBadge","BACKEND_SANDBOX_ENDPOINTS_1009"]:
        if marker not in text: raise SystemExit(f"VALIDATION_FAILED missing html marker {marker}")
    node=shutil.which("node")
    if node:
        scripts="\n".join(re.findall(r"(?s)<script>(.*?)</script>", text))
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as f:
            f.write(scripts); temp=f.name
        proc=subprocess.run([node,"--check",temp],capture_output=True,text=True)
        if proc.returncode != 0: raise SystemExit("VALIDATION_FAILED js syntax")
def check_adapter(root):
    p=root/"backend/xiaobei_ai/xiaojiao_preview_sandbox_store_1009H.py"
    if p.exists():
        proc=subprocess.run(["python","-m","py_compile",str(p)],capture_output=True,text=True)
        if proc.returncode != 0: raise SystemExit("VALIDATION_FAILED adapter syntax")
        text=p.read_text(encoding="utf-8", errors="ignore")
        for marker in ["production_store_enabled", "real_database_written", "estimate_provider_cost"]:
            if marker not in text: raise SystemExit(f"VALIDATION_FAILED adapter marker {marker}")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root", default="."); args=ap.parse_args(); root=Path(args.root)
    for rel in [r for r in REQUIRED if r.strip()]:
        p=root/rel
        if not p.exists(): raise SystemExit(f"VALIDATION_FAILED missing {rel}")
        if p.suffix.lower() != ".zip" and not no_secret(p): raise SystemExit(f"VALIDATION_FAILED possible secret leakage {rel}")
    result=load(root/"docs/audit"/f"{SLUG}_result.json")
    foundation=load(root/"docs/foundation"/f"{SLUG}.json")
    manifest=load(root/"docs/audit_packages"/f"{SLUG}_manifest.json")
    if result.get("final_status") != FINAL_STATUS or result.get("pass") is not True: raise SystemExit("VALIDATION_FAILED status")
    if result.get("marker") != MARKER: raise SystemExit("VALIDATION_FAILED marker")
    flags={"preview_route_only":True,"backend_sandbox_store_enabled":True,"real_database_written":False,"production_store_enabled":False,"memory_written":False,"Feishu_written":False,"formal_apply_performed":False,"default_route_changed":False,"teacher_review_required":True,"batch_generation_allowed":False,"background_generation_allowed":False,"default_route_auto_provider_call_allowed":False}
    for k,v in flags.items():
        if result.get(k) is not v: raise SystemExit(f"VALIDATION_FAILED result {k}")
        if foundation.get(k) is not v: raise SystemExit(f"VALIDATION_FAILED foundation {k}")
    check_html(root); check_adapter(root)
    with zipfile.ZipFile(root/"docs/audit_packages"/f"{SLUG}.zip") as zf:
        names=sorted(zf.namelist())
    if names != sorted(manifest.get("entries") or []): raise SystemExit("VALIDATION_FAILED manifest zip mismatch")
    if manifest.get("manifest_minus_zip") != [] or manifest.get("zip_minus_manifest") != []: raise SystemExit("VALIDATION_FAILED manifest diffs")
    for name in names:
        if "\\" in name or name.startswith("/") or ":" in name: raise SystemExit(f"VALIDATION_FAILED bad zip path {name}")
        lower=name.lower()
        if any(f in lower for f in FORBIDDEN): raise SystemExit(f"VALIDATION_FAILED forbidden zip path {name}")
    print(MARKER)
if __name__=="__main__": main()

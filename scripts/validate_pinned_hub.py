"""Integration test calls real, pinned TheHub validator in a temporary directory."""
import json
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc6_hub_export import build_fixture

def main():
    if len(sys.argv)!=2:raise SystemExit("Usage: validate_pinned_hub.py <pinned-hub-checkout>")
    hub=Path(sys.argv[1]).resolve()
    if not (hub/"src/hub/validate.py").is_file():raise RuntimeError("missing pinned Hub code")
    sys.path.insert(0,str(hub/"src"))
    from hub.manifest import validate_repo_manifest
    from hub.validate import validate_package
    repo=json.loads((ROOT/"federation.json").read_text())
    assert validate_repo_manifest(repo)==[], "producer manifest rejected by Hub"
    with tempfile.TemporaryDirectory() as temporary:
        p=Path(temporary)
        build_fixture(p,["2024-test","2028-test"])
        errors=validate_package(p,validate_rows=True)
        if errors:raise AssertionError("Hub consumer rejected synthetic fixture: "+repr(errors))
        source=p/"sources.jsonl"
        original=source.read_bytes()
        source.write_bytes(original.replace(b'"source_type":"synthetic_electoral_test"',b'"source_type":3'))
        if not validate_package(p,validate_rows=True):raise AssertionError("Hub failed to detect damaged source and hash")
        source.write_bytes(original)
        manifest_path=p/"manifest.json"
        manifest=json.loads(manifest_path.read_text())
        manifest["files"][0]["record_count"]+=1
        manifest_path.write_text(json.dumps(manifest))
        if not any("record_count mismatch" in e for e in validate_package(p,validate_rows=True)):raise AssertionError("Hub failed to detect count mismatch")
    print("PINNED_HUB_CONSUMER_PASS: manifest, synthetic rows, corruption, count closure")

if __name__=="__main__":main()

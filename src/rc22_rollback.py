"""RC22 disposable multi-repository rollback rehearsal.

Creates all Git repositories inside one temporary directory. Never clones or
writes actual Federation repositories. Verifies independent before/after trees
and fail-closed restoration after one simulated interrupted update.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import run
from hashlib import sha256
import json

REPOS=("transparencia-electoral-pr","centinelas-pr","moneysweep-pr","spiderweb-pr","thehub-pr")

def _git(cwd,*args,check=True):
    p=run(["git","-C",str(cwd),*args],capture_output=True,text=True,check=check)
    if check and p.returncode:raise RuntimeError(p.stderr)
    return p.stdout.strip()

def _digest(path):
    files=sorted(p for p in path.rglob("*") if p.is_file() and ".git" not in p.parts)
    payload=json.dumps([(str(p.relative_to(path)),sha256(p.read_bytes()).hexdigest()) for p in files],
                       ensure_ascii=False,separators=(",",":"),sort_keys=True).encode()
    return sha256(payload).hexdigest()

def rehearse_rollback(*,interrupt_at=2):
    if type(interrupt_at) is not int or not 0<=interrupt_at<len(REPOS):
        raise ValueError("invalid simulated failure location")
    with TemporaryDirectory(prefix="meta2028-disposable-") as tmp:
        root=Path(tmp)
        initial={}
        for name in REPOS:
            p=root/name;p.mkdir();_git(p,"init","-q")
            _git(p,"config","user.name","Synthetic CI Fixture")
            _git(p,"config","user.email","fixture@example.invalid")
            (p/"source.json").write_text(json.dumps({"repo":name,"revision":"baseline"},sort_keys=True))
            _git(p,"add","source.json");_git(p,"commit","-qm","fixture initial baseline")
            initial[name]={"commit":_git(p,"rev-parse","HEAD"),"digest":_digest(p)}
        altered=[]
        for i,name in enumerate(REPOS):
            p=root/name
            (p/"source.json").write_text(json.dumps({"repo":name,"revision":"candidate"},sort_keys=True))
            _git(p,"add","source.json");_git(p,"commit","-qm","fixture provisional update")
            altered.append(name)
            if i==interrupt_at:break
        for name in REPOS:
            p=root/name
            _git(p,"reset","--hard",initial[name]["commit"])
            if _git(p,"rev-parse","HEAD")!=initial[name]["commit"] or _digest(p)!=initial[name]["digest"]:
                raise AssertionError("disposable rollback content or commit differs")
            if _git(p,"status","--porcelain"):
                raise AssertionError("uncommitted files after rollback")
        return {"fixture_repositories":len(REPOS),"modified_before_failure":len(altered),
                "restored":len(REPOS),"commit_and_content_parity":"PASS",
                "real_repository_refs_affected":0,"production_rollback_verified":False,
                "status":"DISPOSABLE_FIXTURE_PASS_ONLY"}

#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission_build"
STATIC = OUT / "Static_Website"
SOURCE_ZIP = OUT / "Shoufeng_Chen_Portfolio_Source.zip"
FINAL_ZIP = ROOT / "Shoufeng_Chen_AD688_Portfolio_Submission.zip"
QUARTO = Path.home() / ".local" / "bin" / "quarto"

EXCLUDED_DIRS = {
    ".git", ".venv", "_site", "submission_build",
    ".quarto", "_freeze", "__pycache__"
}
EXCLUDED_FILES = {
    FINAL_ZIP.name, ".DS_Store"
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}

print("[1/5] Rendering Quarto website...")
subprocess.run([str(QUARTO), "render"], cwd=ROOT, check=True)

print("[2/5] Preparing clean submission workspace...")
if OUT.exists():
    shutil.rmtree(OUT)
if FINAL_ZIP.exists():
    FINAL_ZIP.unlink()
STATIC.parent.mkdir(parents=True, exist_ok=True)

print("[3/5] Copying static website...")
shutil.copytree(ROOT / "_site", STATIC)

def include_source(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_FILES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()

print("[4/5] Building source-code archive...")
with zipfile.ZipFile(SOURCE_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(ROOT.rglob("*")):
        if include_source(path):
            zf.write(path, path.relative_to(ROOT))

print("[5/5] Building final submission archive...")
with zipfile.ZipFile(FINAL_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(STATIC.rglob("*")):
        if path.is_file():
            arc = Path("Static_Website") / path.relative_to(STATIC)
            zf.write(path, arc)
    zf.write(SOURCE_ZIP, SOURCE_ZIP.name)

print()
print(f"Created: {FINAL_ZIP}")
print(f"Static files: {sum(1 for p in STATIC.rglob('*') if p.is_file())}")
with zipfile.ZipFile(SOURCE_ZIP) as zf:
    names = zf.namelist()
    print(f"Source files: {len(names)}")
    required = [
        "index.qmd", "projects.qmd", "ad688.qmd",
        "cv.qmd", "contact.qmd", "_quarto.yml",
        "styles.css", "requirements.txt",
        ".github/workflows/quarto-publish.yml"
    ]
    missing = [name for name in required if name not in names]
    if missing:
        raise SystemExit(f"Missing required source files: {missing}")
    print("Required source files: OK")

with zipfile.ZipFile(FINAL_ZIP) as zf:
    names = zf.namelist()
    for required in [
        "Static_Website/index.html",
        "Static_Website/projects.html",
        "Static_Website/ad688.html",
        "Static_Website/cv.html",
        "Static_Website/contact.html",
        SOURCE_ZIP.name,
    ]:
        if required not in names:
            raise SystemExit(f"Missing from final package: {required}")
    print("Final package structure: OK")
    print(f"Final package size: {FINAL_ZIP.stat().st_size / 1024 / 1024:.2f} MB")

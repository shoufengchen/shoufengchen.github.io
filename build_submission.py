#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
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
DATA_SUFFIXES = {".csv", ".parquet", ".xlsx", ".xls", ".feather", ".pkl"}

def is_sensitive_name(name: str) -> bool:
    return name == ".env" or name.startswith(".env.")

def include_source(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_FILES or is_sensitive_name(path.name):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()

class LocalRefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.refs.append(value)

def validate_static_links(root: Path):
    broken = []
    checked = 0
    html_files = sorted(root.rglob("*.html"))

    for html in html_files:
        parser = LocalRefParser()
        parser.feed(html.read_text(encoding="utf-8", errors="replace"))

        for raw in parser.refs:
            if raw.startswith((
                "#", "http://", "https://", "mailto:", "tel:",
                "javascript:", "data:"
            )):
                continue

            path = unquote(urlsplit(raw).path)
            if not path:
                continue

            target = (
                root / path.lstrip("/")
                if path.startswith("/")
                else html.parent / path
            )
            if path.endswith("/"):
                target = target / "index.html"

            checked += 1
            if not target.exists():
                broken.append((html.relative_to(root), raw))

    if broken:
        sample = "; ".join(f"{page}: {ref}" for page, ref in broken[:10])
        raise SystemExit(
            f"Broken local references in static website ({len(broken)}): {sample}"
        )

    return len(html_files), checked

print("[1/6] Cleaning previous render and submission artifacts...")
if OUT.exists():
    shutil.rmtree(OUT)
if SITE.exists():
    shutil.rmtree(SITE)
if FINAL_ZIP.exists():
    FINAL_ZIP.unlink()

print("[2/6] Rendering Quarto website from a clean output directory...")
subprocess.run([str(QUARTO), "render"], cwd=ROOT, check=True)

if not (SITE / "index.html").exists():
    raise SystemExit("Quarto render did not produce _site/index.html")

print("[3/6] Copying clean static website...")
STATIC.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(SITE, STATIC)

print("[4/6] Building source-code archive...")
with zipfile.ZipFile(SOURCE_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(ROOT.rglob("*")):
        if include_source(path):
            zf.write(path, path.relative_to(ROOT))

print("[5/6] Validating source and static website...")
static_files = [p for p in STATIC.rglob("*") if p.is_file()]

recursive_artifacts = [
    p for p in static_files
    if "submission_build" in p.relative_to(STATIC).parts
]
if recursive_artifacts:
    raise SystemExit(
        "Recursive submission_build content detected in static website: "
        + str(recursive_artifacts[0])
    )

html_count, local_ref_count = validate_static_links(STATIC)

with zipfile.ZipFile(SOURCE_ZIP) as zf:
    source_names = zf.namelist()

required_source = [
    "index.qmd", "projects.qmd", "ad688.qmd", "ad715.qmd",
    "research-popmart.qmd", "cv.qmd", "contact.qmd",
    "_quarto.yml", "styles.css", "requirements.txt",
    "README.md", "build_submission.py",
    ".github/workflows/quarto-publish.yml"
]
missing_source = [name for name in required_source if name not in source_names]
if missing_source:
    raise SystemExit(f"Missing required source files: {missing_source}")

data_files = [
    name for name in source_names
    if Path(name).suffix.lower() in DATA_SUFFIXES
]
if data_files:
    raise SystemExit(f"Course data files found in source archive: {data_files}")

sensitive_files = [
    name for name in source_names
    if is_sensitive_name(Path(name).name)
]
if sensitive_files:
    raise SystemExit(f"Sensitive environment files found in source archive: {sensitive_files}")

print("[6/6] Building final submission archive...")
with zipfile.ZipFile(FINAL_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(STATIC.rglob("*")):
        if path.is_file():
            arc = Path("Static_Website") / path.relative_to(STATIC)
            zf.write(path, arc)
    zf.write(SOURCE_ZIP, SOURCE_ZIP.name)

with zipfile.ZipFile(FINAL_ZIP) as zf:
    final_names = zf.namelist()

required_final = [
    "Static_Website/index.html",
    "Static_Website/projects.html",
    "Static_Website/ad688.html",
    "Static_Website/ad715.html",
    "Static_Website/research-popmart.html",
    "Static_Website/cv.html",
    "Static_Website/contact.html",
    "Static_Website/assets/Shoufeng_Chen_CV.pdf",
    SOURCE_ZIP.name,
]
missing_final = [name for name in required_final if name not in final_names]
if missing_final:
    raise SystemExit(f"Missing from final package: {missing_final}")

print()
print(f"Created: {FINAL_ZIP}")
print(f"Static files: {len(static_files)}")
print(f"HTML pages: {html_count}")
print(f"Local HTML refs checked: {local_ref_count}")
print(f"Source files: {len(source_names)}")
print("Required source files: OK")
print("Course data files excluded: OK")
print("Sensitive .env files excluded: OK")
print("Broken local links: NONE")
print("Recursive submission artifacts: NONE")
print("Final package structure: OK")
print(f"Final package size: {FINAL_ZIP.stat().st_size / 1024 / 1024:.2f} MB")

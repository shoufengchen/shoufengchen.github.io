# Shoufeng Chen — Analytics Portfolio

Professional portfolio website for **BU MET Applied Business Analytics**, built with **Quarto** on the assigned **AWS EC2** environment and deployed through **GitHub Actions + GitHub Pages**.

**Live site:** https://shoufengchen.github.io

## Development workflow

The portfolio is developed through:

**VS Code Remote SSH → AWS EC2 → Quarto `.qmd` source → `quarto render` → GitHub → GitHub Actions → GitHub Pages**

Primary EC2 workspace:

```text
/home/ubuntu/shoufengchen.github.io
```

The repository contains source code and presentation assets only. Course data files such as CSV, Parquet, and Excel datasets are intentionally excluded.

## Assignment requirements mapping

| Requirement | Implementation |
|---|---|
| About You | `index.qmd` |
| Projects | `projects.qmd` |
| CV + downloadable PDF | `cv.qmd` + `assets/Shoufeng_Chen_CV.pdf` |
| Contact | `contact.qmd` |
| Professional project visuals | AD688 charts + structured case-study layouts |
| Quarto source | All portfolio pages are authored as `.qmd` files |
| GitHub repository | This repository |
| Hosted website | GitHub Pages |
| Static website submission | Generated from `_site/` |
| Source-code ZIP | Generated automatically by `build_submission.py` |
| Exclude data files | No CSV / Parquet / XLSX course datasets are tracked |

The portfolio intentionally does **not** use standalone “Data Cleaning” or “Data Exploration” tabs. Analytical work is presented as employer-facing case studies.

## Featured case studies

### AD688 — Employability Analytics

**Source:** `ad688.qmd`

Large-scale labor-market analytics using:

- **815,193** job postings
- **51,795** companies
- **20** Parquet files
- PySpark
- Spark SQL
- AWS EC2
- Quarto

Detailed page: https://shoufengchen.github.io/ad688.html

### AD715 — Microbrewery Investment Feasibility

**Source:** `ad715.qmd`

Investment and operating analysis for a proposed **$150,000** Boston restaurant microbrewery, including:

- strategy analysis
- demand and capacity planning
- channel contribution
- break-even analysis
- financing assumptions
- sensitivity and risk analysis
- conditional go/no-go recommendation

Detailed page: https://shoufengchen.github.io/ad715.html

### Published Research — POP MART Consumer Psychology

**Source:** `research-popmart.qmd`

Published research applying Prospect Theory, Cognitive Dissonance, and Maslow's Hierarchy to blind-box consumer behavior and brand strategy.

Detailed page: https://shoufengchen.github.io/research-popmart.html

DOI: https://doi.org/10.54097/135s5t77

## Main source files

```text
_quarto.yml
index.qmd
projects.qmd
ad688.qmd
ad715.qmd
research-popmart.qmd
cv.qmd
contact.qmd
styles.css
requirements.txt
build_submission.py
.github/workflows/quarto-publish.yml
```

## Render on AWS EC2

```bash
cd ~/shoufengchen.github.io
source .venv/bin/activate
quarto render
```

The rendered static website is written to:

```text
_site/
```

## GitHub Actions deployment

Every push to `main` triggers:

1. Checkout
2. Python 3.12 setup
3. Install dependencies from `requirements.txt`
4. Quarto setup
5. `quarto render`
6. Upload the `_site` artifact
7. Deploy to GitHub Pages

Workflow:

```text
.github/workflows/quarto-publish.yml
```

## Submission packaging

Run on EC2:

```bash
python3 build_submission.py
```

This creates:

```text
Shoufeng_Chen_AD688_Portfolio_Submission.zip
├── Static_Website/
│   ├── index.html
│   ├── projects.html
│   ├── ad688.html
│   ├── ad715.html
│   ├── research-popmart.html
│   ├── cv.html
│   ├── contact.html
│   ├── assets/
│   └── site_libs/
└── Shoufeng_Chen_Portfolio_Source.zip
```

The source archive excludes `.git`, `.venv`, rendered `_site` files, generated submission artifacts, and course datasets.

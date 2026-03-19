<div align="center">

<img src="img/artisancoder.png" alt="CraftCoding" width="120"/>

# CraftCoding

**Monitor your coding sessions. Prove every line is yours.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Built with AI](https://img.shields.io/badge/Built%20with-AI%20%F0%9F%98%87-D4AF37?style=flat-square)](https://github.com)

*Yes, this anti-AI tool was built with AI. The irony is very much intentional.*

</div>

---

## What is CraftCoding?

CraftCoding is a desktop application that runs silently while you code. It watches your windows, browser tabs, and running processes every second. The moment it spots an AI tool — ChatGPT, Cursor, Copilot, or anything else — it fires an alert, docks your score, and in Strict Mode redirects you.

When you close a project, you get a **signed PNG certificate** with your stats and one of three medal seals:

<div align="center">

| 🥇 Artisan Coder | 🥈 Hybrid Coder | ❌ Vibe Coder |
|:---:|:---:|:---:|
| 0 detections · score ≥ 90% | Used hints or score ≥ 50% | Score < 50% |
| Pure human logic | Partially assisted | AI did the thinking |

</div>

---

## Why does this exist?

During my second year of cross-platform application development studies, I started noticing a worrying pattern: students were handing their problem-solving over to AI entirely — often without understanding what came back.

AI is a powerful tool. The issue is **unconscious dependency**. CraftCoding makes the choice deliberate. You can still ask for help — it just costs you points and downgrades your seal.

> *The certificate is not a judgment. It is a record.*

---

## Features

<details>
<summary><b>🔒 Project Sealing</b></summary>
<br>
Name your project and seal it before starting. The timer only runs while sealed — your tracked time is honest. Unseal at any time to pause everything and save progress.
</details>

<details>
<summary><b>⏱ Live Session Timer</b></summary>
<br>
A large monospace timer counts every second of active coding. Pause any time — progress saves automatically to a local SQLite database and resumes exactly where you left off, even across restarts.
</details>

<details>
<summary><b>🕵️ 4-Layer AI Detection</b></summary>
<br>

CraftCoding runs four detection layers every second:

| # | Layer | What it catches |
|---|-------|-----------------|
| 1 | **All open windows** | Every window title on your desktop — not just the active one. Catches renamed chat tabs like `"How to reverse a linked list — ChatGPT"` |
| 2 | **Browser process args** | Command-line arguments of Chrome, Edge, and Brave looking for AI domains |
| 3 | **Native AI processes** | `cursor.exe`, `windsurf`, `copilot`, `tabnine`, `codeium`, `ollama`, and more via `psutil` |
| 4 | **Live session files** | The `Sessions/Tabs_*` files Edge and Chrome write in real time — detects open tabs even when the title has completely changed. Only reads files fresher than 5 minutes and only if the browser is actually running |

**No false positives from closed tabs** — the history database is intentionally not used.
</details>

<details>
<summary><b>🚨 Alert Toast + Strict Mode</b></summary>
<br>

When AI is detected a toast notification appears at the top of your screen with a 5-second countdown.

- **Friendly mode** — warning only, −5 pts
- **Strict mode** — closes the AI tab and redirects to Stack Overflow, −5 pts

</details>

<details>
<summary><b>📊 Human Score</b></summary>
<br>

Starts at 100%. A live progress bar in the sidebar tracks it — green above 70, orange above 40, red below.

- AI detection → **−5 pts**
- Emergency hint → **−10 pts**

</details>

<details>
<summary><b>🆘 Emergency Mode</b></summary>
<br>

Completely stuck? You can voluntarily request a hint. This immediately downgrades your seal to **Hybrid Coder**, deducts 10 points, and gets logged in the final certificate. No hiding it.
</details>

<details>
<summary><b>🏆 Certificate Generation</b></summary>
<br>

A 1600×820 PNG certificate with:
- Project name, total coding time, Human Score, detection count
- Your medal image
- Unique certificate ID
- Color theme (gold / blue / red) matching your seal

</details>

<details>
<summary><b>📂 Project Library</b></summary>
<br>

A full project manager window. Search, filter by status (In Progress / Certified), reopen projects, or delete them. Each card shows a color-coded status stripe and all stats at a glance.
</details>

---

## Installation

### Prerequisites

- Python **3.10 or higher**
- Windows 10 / 11 *(detection layers 2–4 are Windows-specific)*

### 1 — Clone the repo

```bash
git clone https://github.com/yourusername/craftcoding.git
cd craftcoding
```

### 2 — Install dependencies

```bash
pip install customtkinter pygetwindow pyautogui psutil Pillow
```

<details>
<summary>Optional: Firefox session detection</summary>

```bash
pip install lz4
```
</details>

### 3 — Add your medal images

Place the three medal PNGs in an `img/` folder next to the script:

```
craftcoding/
├── craftcoding.py
├── craftcoding.db        ← created automatically on first run
└── img/
    ├── artisancoder.png
    ├── hybridprogramer.png
    └── vibecoder.png
```

### 4 — Run

```bash
python craftcoding.py
```

---

## How to use it

```
1. Type your project name  ──▶  Press Enter or click SELLAR
                                        │
2. Choose your mode  ────────────────▶  Amable (warnings) or Estricto (closes tabs)
                                        │
3. Click ▶ INICIAR FORJA  ────────────▶  Timer starts. CraftCoding watches.
                                        │
4. Code.                                │
                                        │
5. Click ⏸ PAUSAR  ─────────────────▶  Progress saves automatically.
                                        │
6. Click 🏆 CERTIFICAR  ─────────────▶  Get your seal. Export your certificate.
```

> Your project library is always accessible from the sidebar with **📂 Mis Proyectos**.
> You can close and reopen the app at any time — everything is saved.

---

## Detection accuracy

| Scenario | Result |
|----------|--------|
| ChatGPT open with a renamed chat title | ✅ Detected — window title scan |
| Claude in an Edge tab in the background | ✅ Detected — session file scan |
| Cursor IDE running | ✅ Detected — process scan |
| GitHub Copilot active in VS Code | ✅ Detected — process scan |
| ChatGPT visited 20 min ago, tab now closed | ✅ Not detected — history scan intentionally removed |
| Edge closed, old session file on disk | ✅ Not detected — 5-minute freshness check |
| Ollama running locally | ✅ Detected — process scan |

---

## Project structure

```
craftcoding.py        Entry point and full application
craftcoding.db        SQLite database (auto-created, auto-migrated)
img/                  Medal images used in certificate generation
```

The database stores: project name · total seconds · Human Score · AI detection count · status · start/end dates · seal type.
Schema migrations run automatically — old databases update without data loss.

---

## Tech stack

| Library | Role |
|---------|------|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern dark-mode desktop UI |
| [psutil](https://github.com/giampaolo/psutil) | Process monitoring |
| [PyGetWindow](https://github.com/asweigart/pygetwindow) | Window title scanning |
| [PyAutoGUI](https://github.com/asweigart/pyautogui) | Tab redirection in Strict mode |
| [Pillow](https://python-pillow.org/) | Certificate PNG generation |
| SQLite3 | Local project database (stdlib) |

---

<div align="center">

**CraftCoding** — because the best code is the code you actually understand.

</div>

# DAY 0 SETUP — Exact Instructions

Goal: finish all environment/repository setup today so Day 1 contains actual AI learning.

Do the steps in order. If a command fails, stop at that step and paste the error into ChatGPT.

---

## Step 1 — Put the starter project somewhere permanent

Recommended folder name:

```text
ai-incident-copilot
```

Do not keep the working repo inside Downloads.

Example macOS/Linux location:

```bash
mkdir -p ~/projects
cd ~/projects
```

Example Windows PowerShell location:

```powershell
New-Item -ItemType Directory -Force "$HOME\projects" | Out-Null
Set-Location "$HOME\projects"
```

Move/extract this starter folder there and rename it to `ai-incident-copilot`.

Then `cd` into it.

---

## Step 2 — Environment fingerprint FIRST

### macOS

Run:

```bash
sw_vers
uname -m
sysctl -n hw.memsize
git --version
docker --version
docker compose version
ollama --version
uv --version
```

Some commands may say `command not found`; that is useful information.

### Windows PowerShell

Run:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsArchitecture, CsTotalPhysicalMemory
git --version
docker --version
docker compose version
ollama --version
uv --version
```

Send the complete output to ChatGPT before proceeding with compatibility-sensitive installs.

---

## Step 3 — Git

If Git already works, skip installation.

Initialize repository:

```bash
git init
git branch -M main
git status
```

Set identity only if Git tells you it is missing:

```bash
git config --global user.name "YOUR NAME"
git config --global user.email "YOUR GITHUB EMAIL"
```

Do not commit yet; first finish the baseline environment.

---

## Step 4 — Python environment with uv

We use `uv` for Python version/environment/dependency management.

If `uv` is missing:

### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a fresh terminal afterward if `uv` is not immediately found.

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```bash
uv --version
```

Install Python 3.12:

```bash
uv python install 3.12
```

Create/sync project environment:

```bash
uv sync
```

Verify:

```bash
uv run python --version
uv run pytest
```

Expected baseline:
- Python reports 3.12.x
- pytest passes the starter test

---

## Step 5 — IDE

Preferred for this project:
- IntelliJ IDEA is acceptable if you already use it.
- Ensure the official Python plugin is installed/enabled.

Open the **repository root**, not an individual Python file.

Configure interpreter to the repository virtual environment:

```text
<repo>/.venv
```

If IntelliJ does not detect it automatically:
1. Settings / Project Structure
2. Python SDK
3. Add existing interpreter
4. Choose the `.venv` Python executable

Do not install random Python packages from the IDE UI. Dependencies should be declared through the project environment.

---

## Step 6 — Docker

Do not install PostgreSQL, Redis or Kafka directly on your laptop. We will later run learning infrastructure as containers.

If Docker already works:

```bash
docker version
docker compose version
docker run --rm hello-world
```

If Docker is missing, follow the official Docker Desktop installer appropriate for your OS/CPU.

Important:
- On macOS, compatibility depends on the macOS version.
- If current Docker Desktop is unsupported on the machine, document it in `PROJECT_STATE.md` and ask ChatGPT for the fallback instead of forcing an old random installer.

---

## Step 7 — Ollama

If Ollama already works:

```bash
ollama --version
```

Do **not** download a large model tonight unless ChatGPT selects one based on your machine RAM/CPU/GPU.

If Ollama is missing:
- macOS: compatibility depends on macOS version; current releases require a supported macOS.
- Windows: use the official installer.
- If unsupported, we will choose a different local inference route or a tiny hosted/free path.

The model choice is deliberately postponed until ChatGPT sees the environment fingerprint.

---

## Step 8 — Baseline repository test

Run:

```bash
uv run pytest
```

Then:

```bash
git status
```

Review that no secrets, huge models or environment folders are staged/tracked.

---

## Step 9 — Create GitHub repository

Create a new GitHub repository named:

```text
ai-incident-copilot
```

Recommended:
- Public, if you are comfortable making the learning project visible to recruiters.
- Do NOT auto-create README, `.gitignore`, or license on GitHub because they already exist locally.

Then GitHub will show a remote URL. Add it:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git remote -v
```

---

## Step 10 — Day 0 documentation update

Tell ChatGPT:

> Environment setup is complete. Here is my environment fingerprint and the output of `uv run pytest`, `git status`, and `git remote -v`. Check Day 0 Definition of Done and give me exact PROJECT_STATE.md updates plus the Day 0 commit commands.

Only mark items complete that actually succeeded.

---

## Step 11 — Commit and push

Typical checkpoint:

```bash
git add .
git commit -m "day-00: initialize AI engineer capstone"
git push -u origin main
```

Then:

```bash
git status
```

Expected:

```text
nothing to commit, working tree clean
```

Day 0 is then complete.

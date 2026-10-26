# Hosting & Deployment Guide — Malayalam Compiler IDE

This guide details the **best platforms** to host this Flask-based Malayalam Compiler Web IDE for free, with continuous deployment and custom domain support.

---

## 🏆 Top Recommendation: Render (render.com)
**Why it's the best option:**
* **100% Free Web Service tier** with automatic HTTPS (`https://your-project.onrender.com`).
* **Continuous Git Deployment**: Push code to GitHub ➔ Render builds and redeploys automatically.
* **Native Python Environment**: Autodetects `requirements.txt` and starts with `gunicorn app:app` via [Procfile](file:///Users/apple/Desktop/CD%20Microproject/Procfile).
* Pre-configured blueprint included via [render.yaml](file:///Users/apple/Desktop/CD%20Microproject/render.yaml).

### Step-by-Step Deployment on Render:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Malayalam Compiler Web IDE"
   git branch -M main
   git remote add origin https://github.com/<your-username>/malayalam-compiler-ide.git
   git push -u origin main
   ```
2. **Sign up at [render.com](https://render.com)** (Sign in with your GitHub account).
3. **Create New Web Service**:
   * Click **New +** ➔ **Web Service**.
   * Select your `malayalam-compiler-ide` repository.
4. **Configure Settings**:
   * **Name**: `malayalam-compiler` (or your choice)
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
   * **Instance Type**: `Free`
5. **Add Environment Variable (Optional)**:
   * Key: `GROQ_API_KEY`
   * Value: `gsk_...` (Your Groq API key)
6. Click **Deploy Web Service**!
   * Within ~2 minutes, your web IDE is live at `https://malayalam-compiler.onrender.com`.

---

## 🥈 Second Best: Railway (railway.app)
**Why choose Railway:**
* Super-fast zero-configuration deployments.
* Automatic HTTPS and live streaming logs.
* Free monthly trial credits.

### Step-by-Step Deployment on Railway:
1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select this repository.
4. Railway will automatically detect Python, install dependencies from `requirements.txt`, and execute `gunicorn app:app`.
5. Under project **Variables**, add `GROQ_API_KEY` if desired.
6. Under project **Settings** ➔ **Networking**, click **Generate Domain** to get your public `.up.railway.app` URL.

---

## 🥉 Academic & Free Alternative: PythonAnywhere (pythonanywhere.com)
**Great for university evaluations / college submissions:**
* Dedicated specifically to Python Flask/Django web apps.
* Doesn't spin down like some serverless tiers.

### Step-by-Step Deployment on PythonAnywhere:
1. Sign up for a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Consoles** tab and open a **Bash console**.
3. Clone your GitHub repository or upload your zip file:
   ```bash
   git clone https://github.com/<your-username>/malayalam-compiler-ide.git
   cd malayalam-compiler-ide
   pip3 install --user -r requirements.txt
   ```
4. Go to the **Web** tab:
   * Click **Add a new web app**.
   * Choose **Flask** and select **Python 3.10** (or Manual configuration).
   * Set the Path to your code: `/home/<username>/malayalam-compiler-ide`.
   * Edit the WSGI configuration file:
     ```python
     import sys
     path = '/home/<username>/malayalam-compiler-ide'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
5. Click **Reload <username>.pythonanywhere.com**!

---

## 🐳 Docker Deployment (For any Cloud VM / AWS / GCP / DigitalOcean)
If hosting on your own Linux server or VPS:
1. Build container:
   ```bash
   docker build -t malayalam-compiler .
   ```
2. Run container:
   ```bash
   docker run -d -p 5050:5050 -e GROQ_API_KEY="gsk_..." malayalam-compiler
   ```

---

## ⚡ Groq AI Models Supported
The compiler's Educational Multi-Language Studio uses **Non-Llama open-weights models** hosted on Groq:
1. **`qwen/qwen3.8-27b`** *(Default / Recommended)* — Alibaba's state-of-the-art multilingual reasoning model, best for Indic script & code conversion.
2. **`openai/gpt-oss-120b`** — OpenAI's large open-weight reasoning model.
3. **`qwen-qwq-32b`** — Qwen reasoning model optimized for deep coding & mathematical logic.
4. **`openai/gpt-oss-20b`** — Ultra-fast compact reasoning model.

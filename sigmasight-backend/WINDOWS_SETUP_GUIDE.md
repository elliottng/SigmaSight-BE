# 🪟 Windows Setup Guide for SigmaSight Backend

This guide will help you set up the SigmaSight backend on Windows with minimal technical knowledge.

## 📋 What You'll Need

- Windows 10 or 11
- About 30 minutes
- Internet connection
- Administrator access on your computer

## 🎯 Overview

We'll install these tools in order:
1. **Python** - The programming language
2. **Git** - To download the code
3. **Docker Desktop** - To run the database
4. **UV** - To manage Python packages

---

## Step 1: Install Python 🐍

1. **Download Python:**
   - Go to https://python.org/downloads/
   - Click the big yellow "Download Python 3.11.x" button
   - Save the installer

2. **Install Python:**
   - Double-click the downloaded file
   - ⚠️ **IMPORTANT**: Check ✅ "Add Python 3.11 to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Python:**
   - Press `Windows + R`
   - Type `cmd` and press Enter
   - In the black window, type: `python --version`
   - You should see: `Python 3.11.x`
   - Type `exit` to close

---

## Step 2: Install Git 📦

1. **Download Git:**
   - Go to https://git-scm.com/download/win
   - The download should start automatically
   - If not, click "64-bit Git for Windows Setup"

2. **Install Git:**
   - Double-click the downloaded file
   - Click "Next" on all screens (default settings are fine)
   - Click "Install"
   - Click "Finish"

3. **Verify Git:**
   - Open a new Command Prompt (Windows + R, type `cmd`, Enter)
   - Type: `git --version`
   - You should see: `git version 2.x.x`

---

## Step 3: Install Docker Desktop 🐳

1. **Download Docker Desktop:**
   - Go to https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Save the installer

2. **Install Docker Desktop:**
   - Double-click "Docker Desktop Installer.exe"
   - Follow the installation wizard
   - ⚠️ **IMPORTANT**: When prompted, ensure "Use WSL 2" is selected
   - Click "Ok" and wait for installation
   - **Restart your computer** when prompted

3. **Start Docker Desktop:**
   - After restart, Docker Desktop should start automatically
   - If not, find "Docker Desktop" in Start Menu and click it
   - Wait for Docker to fully start (whale icon in system tray turns green)
   - You might see a tutorial - you can skip it

4. **Verify Docker:**
   - Open Command Prompt
   - Type: `docker --version`
   - You should see: `Docker version 2x.x.x`

---

## Step 4: Install UV Package Manager 📚

1. **Open PowerShell as Administrator:**
   - Right-click the Start button
   - Click "Windows PowerShell (Admin)"
   - Click "Yes" if prompted

2. **Install UV:**
   - Copy and paste this command:
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   - Press Enter
   - Wait for installation to complete

3. **Close and Reopen PowerShell:**
   - Type `exit` and press Enter
   - Open a regular PowerShell (not as admin)

4. **Verify UV:**
   - Type: `uv --version`
   - You should see: `uv 0.x.x`

---

## Step 5: Download SigmaSight Code 💻

1. **Create a folder for projects:**
   - Open File Explorer
   - Go to `C:\`
   - Right-click → New → Folder
   - Name it `Projects`

2. **Open Command Prompt in Projects folder:**
   - Navigate to `C:\Projects` in File Explorer
   - Click in the address bar
   - Type `cmd` and press Enter

3. **Download the code:**
   - Copy and paste this command:
   ```bash
   git clone https://github.com/elliottng/SigmaSight-BE.git
   ```
   - Press Enter
   - Wait for download to complete

4. **Navigate to the project:**
   ```bash
   cd SigmaSight-BE\sigmasight-backend
   ```

---

## Step 6: Set Up the Project 🔧

1. **Install Python packages:**
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```
   - This creates a virtual environment and installs all dependencies

2. **Set up configuration:**
   ```bash
   copy .env.example .env
   ```
   - This creates your configuration file

---

## Step 7: Start the Database 🗄️

1. **Start PostgreSQL database:**
   ```bash
   docker-compose up -d
   ```
   - This starts the database in the background
   - First time may take a few minutes to download

2. **Verify database is running:**
   ```bash
   docker ps
   ```
   - You should see a container named `sigmasight-backend_postgres_1` or similar

3. **Set up database tables:**
   ```bash
   uv run alembic upgrade head
   ```
   - This creates all the necessary tables

---

## Step 8: Start SigmaSight 🚀

1. **Start the application:**
   ```bash
   uv run python run.py
   ```

2. **Verify it's working:**
   - Open your web browser
   - Go to http://localhost:8000
   - You should see: `{"message": "SigmaSight Backend API", "version": "1.0.0"}`

3. **View API Documentation:**
   - Go to http://localhost:8000/docs
   - You'll see all available API endpoints

---

## 📝 Daily Usage

After initial setup, here's how to start SigmaSight each day:

1. **Start Docker Desktop** (if not already running)
   - Look for whale icon in system tray

2. **Open Command Prompt**
   - Navigate to project: `cd C:\Projects\SigmaSight-BE\sigmasight-backend`

3. **Start the database:**
   ```bash
   docker-compose up -d
   ```

4. **Start SigmaSight:**
   ```bash
   uv run python run.py
   ```

5. **Stop everything when done:**
   - Press `Ctrl + C` in Command Prompt to stop SigmaSight
   - Run `docker-compose down` to stop the database

---

## 🆘 Troubleshooting

### "python is not recognized"
- Python wasn't added to PATH during installation
- Reinstall Python and make sure to check "Add to PATH"

### "docker is not recognized"
- Docker Desktop isn't running
- Start Docker Desktop from Start Menu

### "Cannot connect to Docker daemon"
- Docker Desktop isn't fully started
- Wait for whale icon to turn green in system tray

### "uv is not recognized"
- Close and reopen Command Prompt after UV installation
- Try running in PowerShell instead

### Database connection errors
- Make sure Docker is running: `docker ps`
- Restart database: `docker-compose down` then `docker-compose up -d`

### Port 8000 already in use
- Another program is using port 8000
- Stop SigmaSight with Ctrl+C and try again

---

## 🎯 Quick Commands Reference

```bash
# Navigate to project
cd C:\Projects\SigmaSight-BE\sigmasight-backend

# Start database
docker-compose up -d

# Stop database
docker-compose down

# Start SigmaSight
uv run python run.py

# Update code from GitHub
git pull

# Install new dependencies
uv pip install -r requirements.txt

# Run database migrations
uv run alembic upgrade head
```

---

## 💡 Tips

- Keep Docker Desktop running in the background
- Create a desktop shortcut to `C:\Projects\SigmaSight-BE\sigmasight-backend`
- Save commonly used commands in a text file for easy copy-paste
- The database data persists even after stopping Docker

---

## 📞 Need Help?

If you get stuck:
1. Take a screenshot of any error messages
2. Note which step you're on
3. Contact the development team

Remember: Everyone was a beginner once. Take your time and follow each step carefully!

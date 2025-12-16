# Setup Guide - Student Management System

## Windows Setup (Recommended)

### Step 1: Install Python
- Download Python 3.9+ from [python.org](https://www.python.org)
- ✅ Check "Add Python to PATH"
- Click Install

### Step 2: Clone/Download Project
```bash
cd C:\
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Application
```bash
cd backend
python app.py
```

### Step 6: Access Application
Open browser: **http://localhost:5000**

---

## Linux/Mac Setup

### Step 1: Install Python
```bash
# Mac
brew install python3

# Linux
sudo apt-get install python3 python3-pip
```

### Step 2: Clone Project
```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Application
```bash
cd backend
python3 app.py
```

### Step 6: Access Application
Open browser: **http://localhost:5000**

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

### Python Not Found
- Ensure Python is added to PATH
- Try `python3` instead of `python`

### Module Not Found
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Issues
```bash
# Delete database to reset
rm backend/students.db

# Restart Flask
python app.py
```

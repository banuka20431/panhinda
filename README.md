<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=50&duration=4000&pause=1000&color=FFFFFF&background=000000&center=true&vCenter=true&width=800&height=100&lines=PANHINDA" alt="panhinda" />
  
  <div style="margin: 20px 0;">
    <img src="https://img.shields.io/github/stars/ImJanindu/panhinda?style=for-the-badge&logo=github&logoColor=white&color=black&labelColor=black" alt="GitHub stars"/>
    <img src="https://img.shields.io/github/forks/ImJanindu/panhinda?style=for-the-badge&logo=github&logoColor=white&color=black&labelColor=black" alt="GitHub forks"/>
    <img src="https://img.shields.io/github/issues/ImJanindu/panhinda?style=for-the-badge&logo=github&logoColor=white&color=black&labelColor=black" alt="GitHub issues"/>
    <img src="https://img.shields.io/github/license/ImJanindu/panhinda?style=for-the-badge&logo=github&logoColor=white&color=black&labelColor=black" alt="GitHub license"/>
  </div>
  
  <p style="font-size: 18px; color: #666; font-weight: 500; margin: 20px 0;">
    A platform to express thoughts, vision, knowledge and humor.
  </p>
</div>

---

# 🚀 Panhinda

<div align="center">
  
  **Created by [USJ FOT UG](https://github.com/banuka20431)**
  
  🗓️ **Created:** 14/05/2025  
  🔄 **Last Updated:** 22/06/2025
  
</div>

## 🌟 Features

- ✨ Modern and responsive design
- 🚀 High performance
- 📱 Mobile-friendly
- 🔒 Secure by default
- 🎨 Customizable themes

---

## 🛠 Technologies Used

- **Flask** – Backend framework
- **SQLAlchemy** – ORM for database access
- **Flask-Migrate** – Database migration tool
- **Tailwind CSS** – CSS framework
- **JavaScript / Alpine.js** – Lightweight frontend scripting
- **npm** – Frontend dependency management

---

## 📂 Project Structure

```
panhinda/
├── app/                # Main application code
├── migrations/         # Database migrations
├── static/             # CSS, JS, and image files
├── templates/          # HTML templates
├── config.py           # Configuration file
├── package.json        # npm configuration
└── ...
```

---

## 🧪 Getting Started

Follow these steps to clone and set up the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/banuka20431/panhinda
cd panhinda
```

### 2. Create and Activate a Virtual Environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 4. Create `config.py`

Create a file named `config.py` in the root directory with the following content:

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask security params
    SECRET_KEY = os.environ.get("SECRET_KEY", 'secret-key')
    
    # Flask SQLAlchemy params
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", f"sqlite:///{os.path.join(basedir, 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"

    # Flask session params
    SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT", "False").lower() == "true"
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")

    # Mail server params
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "***@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "***")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"

    # Custom paths
    USER_DATA_PATH = os.environ.get("USER_DATA_PATH", os.path.join(basedir, "static", "user_data"))
```

> Replace sensitive values (like `MAIL_USERNAME`, `MAIL_PASSWORD`, and `SECRET_KEY`) before deploying.

### 5. Initialize and Migrate the Database

```bash
flask db init
flask db migrate
flask db upgrade
```

### 6. Install Frontend Dependencies

```bash
npm install
npm run watch
```

### 7. Run the Application

```bash
flask run --debug
```

---

## 🤝 Contribution

Contributions are welcome! Feel free to fork this project, submit pull requests, or open issues.

---

## 📄 License

This project is licensed under the [Apache 2.0](LICENSE).

---

<div align="center">
  <strong>⭐ Star this repository if you find it helpful!</strong>
  <br/><br/>
  <a href="https://github.com/ImJanindu/panhinda">
    <img src="https://img.shields.io/badge/View%20on-GitHub-black?style=for-the-badge&logo=github" alt="View on GitHub"/>
  </a>
</div>
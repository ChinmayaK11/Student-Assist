# 📚 StudentAssist

A mobile application built with **KivyMD** and **Firebase** to manage student records efficiently. Allows adding, storing, and viewing student data in real time.

---

## 🚀 Features

- Add student details — name, roll number, and marks
- Auto-calculates percentage from 3 subject marks
- Stores data in **Firebase Realtime Database**
- View all student records with a refresh option
- Clean and simple mobile UI using **KivyMD**

---

## 🛠️ Tech Stack

| Layer      | Technology              |
|------------|--------------------------|
| UI         | KivyMD (Python)          |
| Backend    | Firebase Realtime Database |
| Language   | Python 3                 |

---

## 📁 Project Structure

```
student-assist/
│
├── main.py            # Main app with all screens (Home, Add, View)
├── firebase_config.py # Firebase connection setup
├── view_data.py       # Script to view all student data
├── test_firebase.py   # Script to test Firebase connection
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/student-assist.git
cd student-assist
```

### 2. Install dependencies
```bash
pip install kivymd firebase-admin
```

### 3. Configure Firebase
- Go to [Firebase Console](https://console.firebase.google.com/)
- Create a project and enable **Realtime Database**
- Download your `serviceAccountKey.json`
- Create a `firebase_config.py` file:

```python
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://YOUR_PROJECT_ID.firebaseio.com/'
})

ref = db.reference("students")
```

### 4. Run the app
```bash
python main.py
```

---

## 📸 Screens

| Screen        | Description                          |
|---------------|--------------------------------------|
| Home          | Navigate to Add or View students     |
| Add Student   | Enter name, roll, and 3 subject marks |
| View Students | See all records fetched from Firebase |

---

## 🔒 Note

> `serviceAccountKey.json` and `firebase_config.py` contain sensitive credentials.  
> Add them to `.gitignore` before pushing to GitHub!

```
# .gitignore
serviceAccountKey.json
firebase_config.py
__pycache__/
*.pyc
```

---

## 👨‍💻 Author

Made with ❤️ as a Student Assist Project

# 🎓 AI Mentoring System V2

An AI-powered student mentoring and academic risk analysis platform built using **Flask**, **Python**, **Machine Learning**, and **SQL Server**. The system helps educational institutions identify at-risk students, assign mentors, manage mentoring sessions, and provide AI-assisted guidance.

---

## 🚀 Features

### 👨‍🎓 Student Module
- Student Login
- Student Dashboard
- View Academic Performance
- Book Mentor Sessions
- AI Chatbot Assistance
- Track Mentoring History

### 👨‍🏫 Mentor Module
- Mentor Login
- View Assigned Students
- Manage Bookings
- Student Progress Monitoring

### 👨‍💼 Admin Module
- Secure Admin Login
- Student Management (CRUD)
- Mentor Management (CRUD)
- Booking Management
- Dashboard Analytics
- Reports & Statistics
- Notification System

### 🤖 AI Features
- Student Risk Prediction
- AI Chatbot
- Mentor Recommendation
- Academic Performance Analysis
- Student Risk Index (SRI)

---

# 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Backend
- Python
- Flask

### Database
- Microsoft SQL Server

### Machine Learning
- Scikit-learn
- Pandas
- NumPy
- Joblib

### Visualization
- Matplotlib

---

# 📂 Project Structure

```
AI-Mentoring-System-V2/
│
├── backend/
│   ├── app.py
│   ├── admin.py
│   ├── mentor.py
│   ├── recommendation.py
│   ├── database.py
│   ├── templates/
│   ├── static/
│   └── model.pkl
│
├── data/
│   ├── students.csv
│   ├── mentors.csv
│   └── final_output.csv
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/mahenoorashraf/AI-mentoring-system-V2.git
```

```bash
cd AI-mentoring-system-V2
```

---

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret_key
DATABASE_SERVER=your_server
DATABASE_NAME=your_database
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
```

---

### Run Application

```bash
python backend/app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 📊 Machine Learning

The system predicts students who may require mentoring based on academic and behavioral indicators.

Algorithms and tools used:

- Classification Model
- Feature Scaling
- Risk Score Prediction
- Mentor Recommendation

---

# 📸 Screenshots

You can add screenshots of:

- Login Page
- Admin Dashboard
- Student Dashboard
- Mentor Dashboard
- Reports
- Analytics
- AI Chatbot

---

# 🔒 Security

- Secure Authentication
- Session Management
- Environment Variables
- SQL Database Integration

---

# 🎯 Future Improvements

- Email Notifications
- Video Mentoring
- Attendance Integration
- Real-Time Chat
- Mobile Application
- Cloud Deployment
- Advanced AI Recommendations
- Dashboard Enhancements

---

# 👨‍💻 Author

**Md Noore Jamal**

GitHub:
https://github.com/mahenoorashraf

---

# 📜 License

This project is developed for educational and internship purposes.

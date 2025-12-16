# 📚 Student Management System

A full-stack web application for managing students, tracking attendance, and recording grades. Built as a demonstration of full-stack development skills combining **Python Flask backend** with **vanilla JavaScript frontend**.

**Live Demo:** [Add your deployed link here]  
**GitHub:** [github.com/yourusername/student-management-system](https://github.com/Harshal-Bsys27/student-management-system)  
**Portfolio:** [Add your portfolio website]

---

## 🎯 Project Overview

This project demonstrates **end-to-end full-stack development** capabilities including:
- **Backend API Development** with Flask
- **Database Design & Management** with SQLite
- **Frontend UI/UX** with responsive HTML/CSS/JavaScript
- **Authentication & Authorization** with role-based access
- **Real-time Data Visualization** with Chart.js
- **Professional Code Organization** following best practices

---

## ✨ Key Features

### 👨‍💼 Admin Dashboard
- ✅ **Student Management** - Add, edit, delete, search student records
- ✅ **Attendance Tracking** - Mark, edit, delete attendance with date tracking
- ✅ **Grade Management** - Record marks (0-100), auto-calculate letter grades
- ✅ **User Management** - Manage user roles (Admin/User)
- ✅ **Audit Logging** - Complete action tracking for accountability
- ✅ **Analytics Dashboard** - Visual insights with interactive charts
- ✅ **System Statistics** - Total students, branches, year-wise distribution

### 👤 User Dashboard
- ✅ **View Profile** - Access personal information
- ✅ **Check Attendance** - View attendance history and percentage
- ✅ **View Grades** - See marks, grades, and calculated GPA
- ✅ **Analytics** - Personal performance visualization

### 🔒 Security & Access Control
- ✅ **Role-Based Access Control (RBAC)** - Admin and User roles with different permissions
- ✅ **Secure Authentication** - Password hashing with werkzeug
- ✅ **Session Management** - Secure server-side session handling
- ✅ **Audit Trail** - Complete logging of all admin actions
- ✅ **Input Validation** - Protection against common vulnerabilities

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Semantic markup structure |
| **CSS3** | Modern styling with gradients, animations, flexbox, grid |
| **JavaScript (ES6+)** | Vanilla JS - no frameworks for better understanding |
| **Fetch API** | Async HTTP requests to backend |
| **Chart.js** | Beautiful data visualizations and analytics |
| **Font Awesome 6** | Professional icons (500+ icons) |

### Backend
| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Core server language |
| **Flask** | Lightweight web framework (~50 lines per route) |
| **SQLite3** | Embedded database (perfect for portfolio) |
| **Werkzeug** | Password hashing & security utilities |
| **Flask-CORS** | Cross-origin request handling |

### Development Tools
- **VS Code** - Code editor
- **Postman** - API testing (optional)
- **Git** - Version control

---

## 📊 System Architecture

```
student-management-system/
│
├── backend/ # Flask backend
│ └── app.py
├── templates/ # HTML templates (frontend)
├── static/ # CSS, JS, images
├── requirements.txt
├── .gitignore
└── README.md
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Backend Setup
1. Navigate to the backend directory:
    ```bash
    cd c:\student-management-system\backend
    ```
2. Install the required Python packages:
    ```bash
    pip install flask flask-cors werkzeug
    ```

### Running the Application
- Start the Flask development server:
    ```bash
    python app.py
    ```
- Open your web browser and visit: `http://localhost:5000`

---

## 🚀 Getting Started

1. **First Time Setup**
    - Register as Admin: The first user to register will have admin privileges.
    - Add Students: Admins can add student records manually.
    - Manage Users: Admins can promote other users to admin or restrict access.
    - View Analytics: Access real-time statistics and analytics.

2. **Daily Operations**
    - Admins can manage attendance and grades for students.
    - Users can view their own profiles, attendance, and grades.

---

## 📚 Usage

- **Admin Dashboard**: Overview of student statistics, attendance, and grades.
- **User Management**: Add, edit, or remove users and assign roles.
- **Student Profile**: Detailed view of individual student information, attendance, and grades.
- **Analytics**: Visual representation of data for better insights.

---

## 🔒 Security

- The application uses role-based access control to restrict access to sensitive operations.
- Passwords are securely hashed using Werkzeug's security features.
- All actions are logged for auditability and compliance.

---

## 📈 Future Enhancements

- Implement email notifications for attendance and grade updates.
- Add a calendar view for attendance tracking.
- Integrate with external APIs for extended functionality.

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Make your changes
4. Commit your changes: `git commit -m 'Add your message'`
5. Push to the branch: `git push origin feature/YourFeature`
6. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

For any inquiries or feedback, please reach out:

- **Email**: [your-email@example.com](mailto:your-email@example.com)
- **LinkedIn**: [Your LinkedIn Profile](https://www.linkedin.com/in/yourprofile)

---

Thank you for checking out my project! I hope it demonstrates my skills and passion for full-stack development.

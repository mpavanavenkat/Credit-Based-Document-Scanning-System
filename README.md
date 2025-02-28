# Credit-Based Document Scanning System

📄 **Credit-Based Document Scanning System** allows users to upload, scan, and compare documents based on a credit system. Administrators can manage users, approve credit requests, and track analytics.

---

## 📌 Features

✅ User Authentication: Register/Login securely  
✅ Credit System: Users get a limited number of credits to scan documents  
✅ Document Scanning & Matching: Text similarity comparison using difflib  
✅ Admin Dashboard: Manage users, approve/reject credit requests, view analytics  
✅ Data Storage: SQLite database to store users, scans, and requests  
✅ Fully Responsive UI: Built with TailwindCSS and JavaScript  

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS (TailwindCSS), JavaScript  
- **Backend:** Python (Flask)  
- **Database:** SQLite  
- **Text Similarity Algorithm:** Python’s difflib  
- **Authentication:** JWT (JSON Web Tokens)

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/Credit-Based-Document-Scanning-System.git
cd Credit-Based-Document-Scanning-System


2️⃣ Install Dependencies
Make sure you have Python 3.7+ installed. Then, install the required packages:
cd backend
pip install -r requirements.txt

3️⃣ Setup the Database
Initialize the SQLite database:
python init_db.py
This creates the necessary tables (users, documents, credit_requests, etc.) in app.db.

4️⃣ Generate Test Data (Optional)
To populate the system with sample documents, run:
python generate_test_data.py
This will create sample text files in test_data/.

5️⃣ Run the Backend Server
Start the Flask API:
python app.py
The backend runs at: http://127.0.0.1:5000

6️⃣ Start the Frontend
Run this command to serve the frontend (or directly open index.html):
cd frontend
python -m http.server 8000
Open in browser: http://127.0.0.1:8000/index.html


📝 API Endpoints
Method	Endpoint	Description	Auth Required
POST	/auth/register	Register a new user	❌ No
POST	/auth/login	Login & get JWT token	❌ No
GET	/user/profile	Fetch user details	✅ Yes
POST	/scan	Upload & scan a document	✅ Yes
GET	/admin/users	List all users (Admin only)	✅ Yes
POST	/user/request_credits	Request more credits	✅ Yes
GET	/admin/credit_requests	View pending credit requests	✅ Yes

📸 Screenshots
Login Page - Attached in the screenshots folder
Admin Dashboard - Attached in the screenshots folder

📜 License
This project is licensed under the MIT License.

👨‍💻 Contributor
[Mylavarapu Pavana Venkat] - Developer

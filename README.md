Credit-Based Document Scanning System

📄 Credit-Based Document Scanning System allows users to upload, scan, and compare documents based on a credit system. Administrators can manage users, approve credit requests, and track analytics.

📌 Features \n
✅ User Authentication: Register/Login securely
✅ Credit System: Users get a limited number of credits to scan documents
✅ Document Scanning & Matching: Text similarity comparison using difflib\n
✅ Admin Dashboard: Manage users, approve/reject credit requests, view analytics\n
✅ Data Storage: SQLite database to store users, scans, and requests\n
✅ Fully Responsive UI: Built with TailwindCSS and JavaScript\n

🛠️ Tech Stack\n
Frontend: HTML, CSS (TailwindCSS), JavaScript\n
Backend: Python (Flask)\n
Database: SQLite\n
Text Similarity Algorithm: Python’s difflib\n
Authentication: JWT (JSON Web Tokens)\n

🚀 Getting Started\n
1️⃣ Clone the Repository
git clone https://github.com/YOUR_GITHUB_USERNAME/Credit-Based-Document-Scanning-System.git\n
cd Credit-Based-Document-Scanning-System\n

2️⃣ Install Dependencies\n
Make sure you have Python 3.7+ installed. Then, install the required packages:\n
cd backend\n
pip install -r requirements.txt\n

3️⃣ Setup the Database\n
Initialize the SQLite database:\n
python init_db.py\n
This creates the necessary tables (users, documents, credit_requests, etc.) in app.db.\n

4️⃣ Generate Test Data (Optional)\n
To populate the system with sample documents, run:\n
python generate_test_data.py\n
This will create sample text files in test_data/.\n

5️⃣ Run the Backend Server\n
Start the Flask API:\n
python app.py\n
The backend runs at: http://127.0.0.1:5000\n

6️⃣ Start the Frontend\n
Run this command to serve the frontend (or directly open index.html):\n
cd frontend\n
python -m http.server 8000\n
Open in browser: http://127.0.0.1:8000/index.html\n


📝 API Endpoints\n
Method	Endpoint	Description	Auth Required\n
POST	/auth/register	Register a new user	❌ No\n
POST	/auth/login	Login & get JWT token	❌ No\n
GET	/user/profile	Fetch user details	✅ Yes\n
POST	/scan	Upload & scan a document	✅ Yes\n
GET	/admin/users	List all users (Admin only)	✅ Yes\n
POST	/user/request_credits	Request more credits	✅ Yes\n
GET	/admin/credit_requests	View pending credit requests	✅ Yes\n

📸 Screenshots\n
Login Page - Attached in the screenshots folder\n
Admin Dashboard - Attached in the screenshots folder\n

📜 License\n
This project is licensed under the MIT License.\n

👨‍💻 Contributor
[Mylavarapu Pavana Venkat] - Developer

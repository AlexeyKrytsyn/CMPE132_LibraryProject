### CMPE132 Library Management System  
***Developer:*** Alexey Krytsyn  
***Course:*** CMPE 132 – Information Security  
***Semester:*** Fall 2025  

A Flask-based library management and access control system built for the SJSU Library project. Implements secure authentication, password hashing, and basic role separation between ***Admin***, ***Librarian***, and ***User*** accounts.  

---

### How to Run the Project  

1. ***Clone this repository:***  
   git clone https://github.com/AlexeyKrytsyn/CMPE132_LibraryProject.git  
   cd CMPE132_LibraryProject  

2. ***Create and activate a virtual environment:***  
   python -m venv .venv  
   source .venv/Scripts/activate (Windows Git Bash)  
   or  
   .venv\Scripts\activate (Command Prompt / PowerShell)  

3. ***Install dependencies:***  
   pip install -r requirements.txt  

4. ***Run the application:***  
   python main.py  

5. Open your browser and go to:  
   http://127.0.0.1:5000  

---

### Login Information  

***Admin Account***  
Username: alexeykrytsyn  
Password: alexeykrytsyn  

***What the Admin Can Do:***  
Once logged in at *** /admin *** you can:  
- Add new Librarians  
- View all Users  
- Approve pending user accounts  
- Delete Users  
- Log out securely  

All actions use ***bcrypt-hashed passwords*** and ***Flask session-based authentication***.  

---

### Librarian Account  

- Librarians can log in via *** /Librarian/ *** route using their email and password.  
- The Admin creates Librarian accounts through the Admin dashboard.  
- Librarians can:  
  - Add new books  
  - Delete or update books  
  - View the full library book list  

---

### User Account  

- Users can sign up via *** /user/signup ***  
- After signup, the Admin must approve the account before the user can log in.  
- Once approved, users can:  
  - Log in via *** /user/ ***  
  - Browse available books in the library  

---

### Database Information  

- The app uses ***SQLite (libary.db)*** for local storage.  
- Database tables include:  
  - ***users*** – stores all registered patrons  
  - ***librarian*** – stores librarians added by the admin  
  - ***Admins*** – stores admin login credentials  
  - ***books*** – stores book records (title, genre, optional image)  

---

### Security Features  

- Passwords stored as ***bcrypt hashes*** (never plaintext)  
- Session-based authentication for ***Admin***, ***Librarian***, and ***User*** routes  
- Admin approval process for user accounts  
- Role-based access separation (***Admin → Librarian → User***)


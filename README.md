# 🔐 Password Authentication and Account Lockout System

A Flask-based cybersecurity project demonstrating **secure password authentication, salted password hashing, failed login attempt tracking, and automatic account lockout after three incorrect password attempts**.

This project was developed as a **Project-Based Learning (PBL)** activity for the subject **Cryptography and Network Security**.

---

## 📌 Project Overview

Password authentication is one of the most common methods used to verify user identities. However, insecure password storage and unlimited login attempts can expose systems to password theft and repeated password-guessing attacks.

This project implements a mock authentication system that demonstrates two important security controls:

- Secure password storage using **salted password hashes**
- **Account lockout after three incorrect login attempts**

The system never stores the user's plaintext password in the database.

---

## 🎯 Objectives

The main objectives of this project are to:

- Understand password-based authentication.
- Implement secure user registration and login.
- Store passwords as salted hashes instead of plaintext.
- Verify passwords securely during authentication.
- Track unsuccessful login attempts.
- Automatically lock an account after three incorrect attempts.
- Prevent authentication even with the correct password after an account has been locked.
- Demonstrate controlled account unlocking.
- Independently test and verify the authentication mechanism.

---

## ✨ Features

### 🔐 Secure User Registration

Users can create an account using a username and password.

The password is processed using Werkzeug's password hashing functionality before being stored.

### 🧂 Salted Password Hashing

Plaintext passwords are never stored in the SQLite database.

Instead, the application stores a salted password hash.

Example:

```text
Plaintext Password
        ↓
Password Hashing + Salt
        ↓
Secure Password Hash
        ↓
SQLite Database
```

### 🔑 Secure Login

During login, the entered password is checked against the stored password hash.

```text
Entered Password
       ↓
Password Verification
       ↓
Does it match the stored hash?
       ↓
   YES       NO
    ↓         ↓
 Access    Failed Attempt
```

### 🚫 Three-Attempt Account Lockout

Every incorrect password increases the failed login counter.

```text
Attempt 1 → 2 attempts remaining

Attempt 2 → 1 attempt remaining

Attempt 3 → ACCOUNT LOCKED
```

Once locked, the account cannot authenticate even if the correct password is subsequently entered.

### 🔓 Administrative Unlock

The project contains a demonstration security administration panel.

It allows the account status and failed-attempt counter to be viewed and provides an option to unlock a locked account.

Unlocking resets:

```text
failed_attempts = 0
is_locked = 0
```

The administration interface intentionally does not display passwords or password hashes.

> **Note:** The admin interface is included for academic demonstration. A production application would require proper administrator authentication and authorization.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| Werkzeug | Password hashing and verification |
| SQLite | User authentication database |
| HTML5 | User interface structure |
| CSS3 | User interface styling |
| Python `unittest` | Automated verification |
| Git | Version control |
| GitHub | Source-code repository |

---

## 🏗️ System Architecture

```text
                USER
                  │
                  ▼
          ┌────────────────┐
          │ Flask Web App  │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Authentication │
          │     Logic      │
          └───────┬────────┘
                  │
         ┌────────▼─────────┐
         │ Password Hashing │
         │ & Verification   │
         └────────┬─────────┘
                  │
           ┌──────▼──────┐
           │   SQLite    │
           │  Database   │
           └─────────────┘
```

---

## 🔄 Authentication Flow

```text
                    LOGIN
                      │
                      ▼
              Find User Account
                      │
                      ▼
             Is Account Locked?
                 /          \
               YES           NO
                │             │
          Reject Login        ▼
                       Verify Password
                          /        \
                       MATCH      WRONG
                         │           │
                         ▼           ▼
                    Dashboard   Attempts + 1
                                     │
                                     ▼
                              Attempts >= 3?
                                /        \
                              NO          YES
                              │            │
                         Allow Retry   Lock Account
```

---

## 📂 Project Structure

```text
password-authentication-project/
│
├── app.py
├── verify_database.py
├── test_auth.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin.html
│
└── static/
    └── style.css
```

`users.db` is generated locally and is excluded from the public repository.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/bigblackcoder-coding/password-authentication-account-lockout.git
```

### 2. Enter the project directory

```bash
cd password-authentication-account-lockout
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open the application

Open:

```text
http://127.0.0.1:5000
```

---

## 🧪 Testing

Automated tests are included in:

```text
test_auth.py
```

Run them using:

```bash
python test_auth.py
```

The implemented tests verify:

1. Successful account registration
2. Successful login using the correct password
3. Incorrect-password handling
4. Account lockout after three failed attempts
5. Rejection of the correct password after the account is locked

### Test Result

```text
.....
----------------------------------------------------------------------
Ran 5 tests

OK
```

All **5 test cases passed successfully** during project verification.

---

## 🔍 Database Verification

The project includes:

```text
verify_database.py
```

Run:

```bash
python verify_database.py
```

Example output
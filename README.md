# Authentication System

A complete, production-aware authentication service built with Flask. Covers the full auth lifecycle — registration, login, protected routes, role-based access control, token refresh, and logout with real token invalidation.

Built as a reusable backend module that plugs into future projects.

---

## Features

- User registration with email validation and strong password requirements
- Secure password hashing with bcrypt (salted — safe even if the database leaks)
- JWT-based authentication with access tokens (15 min) and refresh tokens (7 days)
- Protected routes that verify tokens on every request
- Role-based access control — user vs admin routes with a custom decorator
- Token refresh endpoint for silent re-authentication
- Logout with a token blocklist that immediately invalidates tokens server-side
- Minimal HTML/CSS/JS frontend to demo the full auth flow in the browser
- Rate Limiting
- httpOnly cookie for refresh tokens to combat XSS attacks

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask |
| Database | SQLite + SQLAlchemy |
| Password hashing | flask-bcrypt |
| Token management | flask-jwt-extended |
| Frontend | HTML / CSS / Vanilla JS |

---

## Project Structure

```
auth-system/
├── app/
│   ├── __init__.py       # App factory — creates Flask app, registers blueprints
│   ├── models.py         # User and TokenBlocklist database models
│   ├── auth.py           # Register, login, refresh, logout routes
│   ├── protected.py      # Protected and admin-only routes
│   └── extensions.py     # db, bcrypt, jwt objects (avoids circular imports)
├── frontend/
│   └── index.html        # Demo UI
├── config.py             # App settings, token expiry, secret keys
├── run.py                # Entry point
└── requirements.txt
```

---

## Getting Started

**1. Clone and set up the environment**

```bash
git clone https://github.com/edub966/auth-system.git
cd auth-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Run the server**

```bash
python run.py
```

**3. Open the demo UI**

Navigate to `http://127.0.0.1:5000` in your browser.

---

## API Reference

### Auth routes — `/auth`

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/auth/register` | Create a new account | No |
| POST | `/auth/login` | Login and receive tokens | No |
| POST | `/auth/refresh` | Issue a new access token | Refresh token |
| DELETE | `/auth/logout` | Revoke current access token | Access token |

### Protected routes — `/api`

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/api/dashboard` | Returns welcome message for logged-in user | Any user |
| GET | `/api/admin/users` | Returns all registered users | Admin only |

### Example — Register

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Secure123!"}'
```

### Example — Login

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Secure123!"}'
```

### Example — Access a protected route

```bash
curl http://127.0.0.1:5000/api/dashboard \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character (`!@#$%^&*` etc.)

---

## Security Decisions

**Why bcrypt over SHA/MD5?**
bcrypt automatically salts every hash, meaning two identical passwords produce different hashes. SHA and MD5 are fast by design — bcrypt is intentionally slow, which makes brute-force attacks impractical.

**Why JWTs over sessions?**
JWTs are stateless — the server doesn't need to store session data. Any route can verify who the user is without a database lookup on every request, which makes the system easier to scale.

**Why two tokens (access + refresh)?**
The access token expires in 15 minutes. If stolen, the damage window is small. The refresh token lives for 7 days and is only used to silently issue a new access token — it never touches protected routes directly.

**Why a token blocklist for logout?**
JWTs can't be "deleted" — they're valid until they expire. Without a blocklist, logging out on the frontend doesn't actually invalidate the token. Anyone who copied it could keep using it. The blocklist is checked on every protected request, so a logged-out token is dead immediately.

**Why store the access token in memory, not localStorage?**
localStorage is accessible to any JavaScript running on the page, making it vulnerable to XSS attacks. Storing the access token in a JS variable means it's gone when the tab closes — acceptable given its 15-minute lifespan.

---

## Future Improvements

- Swap SQLite for PostgreSQL for production use
- Add email verification on registration
- Dockerize the application

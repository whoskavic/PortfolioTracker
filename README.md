# Portfolio Tracker

A full-stack web application for tracking investment portfolios (crypto & stocks). Monitor positions, analyze trading history, and track PnL with multi-currency support.

## Features

- **Trading History** - Complete log of all buy/sell transactions
- **Current Positions** - Auto-calculated from transaction history
- **PnL Analytics** - 7d, 30d, 1y, and all-time performance
- **Multi-Currency** - Transactions in IDR or USD with real-time conversion
- **JWT Authentication** - Secure user accounts
- **AI OCR** *(coming soon)* - Upload transaction screenshots and extract data automatically
- **TradingView Charts** *(coming soon)* - Live charts for your assets

## Tech Stack

### Backend
- **Python 3.12** — Runtime
- **FastAPI** — Web framework
- **PostgreSQL** — Database (Docker)
- **SQLAlchemy** — ORM
- **JWT + bcrypt** — Authentication
- **ExchangeRate-API** — Real-time IDR/USD conversion
- **Anthropic Claude API** — Future OCR feature

### Frontend
- **React 18** — UI library
- **Vite** — Build tool
- **TailwindCSS 3** — Styling
- **Recharts** — Data visualization
- **React Query** — Server state management
- **Axios** — HTTP client

## Project Structure

```
PortfolioTracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # App setup, middleware, router includes
│   │   ├── deps.py              # Shared auth dependencies (JWT, get_current_user)
│   │   ├── database.py          # PostgreSQL connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── crud.py              # Database operations
│   │   ├── currency_service.py  # Real-time exchange rate service
│   │   └── routers/
│   │       ├── auth.py          # /register, /token, /users/me
│   │       ├── assets.py        # /assets
│   │       ├── transactions.py  # /transactions
│   │       ├── positions.py     # /positions
│   │       └── portfolio.py     # /portfolio/summary
│   ├── REST/                    # HTTP test files
│   │   ├── health-check.http
│   │   ├── auth.http
│   │   ├── assets.http
│   │   ├── transactions.http
│   │   ├── positions.http
│   │   └── portfolio.http
│   ├── venv/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 18+
- Docker Desktop

---

### 1. Start PostgreSQL with Docker

```bash
docker run --name portfolio-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=portfolio_tracker \
  -p 5432:5432 \
  -d postgres:15
```

Verify it's running:
```bash
docker ps
```

To stop/start later:
```bash
docker stop portfolio-postgres
docker start portfolio-postgres
```

---

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and fill in your keys (see Configuration section)
```

---

### 3. Setup Frontend

```bash
cd frontend
npm install
```

---

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

---

## Configuration

### Backend `.env`

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/portfolio_tracker

# Security
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key
EXCHANGE_RATE_API_KEY=your-exchangerate-api-key

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=development
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Register new user | No |
| POST | `/token` | Login (returns JWT) | No |
| GET | `/users/me` | Get current user | Yes |
| GET | `/assets` | List all assets | No |
| POST | `/assets` | Create asset | Yes |
| GET | `/transactions` | Get user transactions | Yes |
| POST | `/transactions` | Create transaction | Yes |
| DELETE | `/transactions/{id}` | Delete transaction | Yes |
| GET | `/positions` | Get current positions | Yes |
| GET | `/portfolio/summary` | PnL analytics | Yes |

Login accepts either **username** or **email** in the `username` field.

---

## Roadmap

- [x] Backend API (auth, transactions, positions, PnL)
- [x] Multi-currency support (IDR/USD)
- [x] JWT authentication
- [x] Auto position calculation
- [ ] Frontend UI (in progress)
- [ ] Image upload & OCR via Claude API
- [ ] TradingView chart integration
- [ ] Real-time price fetching
- [ ] Export to CSV/PDF
- [ ] Alembic database migrations
- [ ] Unit & integration tests
- [ ] Production deployment

---

## Author

**Kavic** — [@whoskavic](https://github.com/whoskavic)

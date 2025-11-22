# 📊 Portfolio Tracker

A comprehensive web application for tracking your investment portfolio. Monitor crypto and stock positions, analyze trading history, and automatically extract transaction data from images using AI-powered OCR.

## ✨ Features

- **📈 Trading History Tracking** - Complete log of all your buy/sell transactions
- **💼 Current Positions** - Real-time view of your active investments
- **📸 Smart Image Upload** - Upload transaction screenshots and let AI extract the data automatically
  - Automatically reads: fees, realized PnL, quantity, price, and more
  - Supports multiple broker formats
- **📊 PnL Analytics** - Track your performance over time
  - 7-day PnL
  - 30-day PnL  
  - 1-year PnL
  - All-time performance
- **📉 TradingView Integration** - Live charts for your assets
- **🎨 Modern Dark UI** - Clean, professional interface optimized for traders

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite/PostgreSQL** - Database (SQLite for dev, PostgreSQL for production)
- **Anthropic Claude API** - AI-powered image analysis and OCR
- **Python 3.12.0** - Recommended version for compatibility

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first styling
- **Recharts** - Data visualization
- **React Query** - Server state management
- **Axios** - HTTP client

## 📁 Project Structure

```
portfolio-tracker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── database.py     # Database configuration
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── crud.py         # Database operations
│   │   └── routers/        # API endpoints
│   ├── venv/               # Virtual environment
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API calls
│   │   └── App.jsx        # Root component
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
│
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/whoskavic/portfolio-tracker.git
cd portfolio-tracker
```

2. **Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

3. **Setup Frontend**
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

4. **Run the application**

Backend (in backend folder):
```bash
uvicorn app.main:app --reload
```

Frontend (in frontend folder):
```bash
npm run dev
```

The backend will run on `http://localhost:8000`  
The frontend will run on `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
DATABASE_URL=sqlite:///./portfolio.db
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:8000
```

## 📸 How to Use Image Upload

1. Take a screenshot of your transaction confirmation from your broker
2. Click "Upload Transaction" in the app
3. Upload the image
4. AI will automatically extract:
   - Asset symbol
   - Transaction type (Buy/Sell)
   - Quantity
   - Price
   - Fees
   - Realized PnL (if applicable)
5. Review and confirm the extracted data
6. Save to your portfolio

## 🗺️ Roadmap

- [x] Project setup and architecture
- [ ] User authentication
- [ ] Manual transaction entry
- [ ] Image upload and OCR processing
- [ ] Current positions dashboard
- [ ] PnL calculations and analytics
- [ ] TradingView chart integration
- [ ] Performance charts and visualizations
- [ ] Export functionality (CSV/PDF)
- [ ] Mobile responsive design
- [ ] Multi-portfolio support
- [ ] Trade notes and tags

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Kavic**
- GitHub: [@whoskavic](https://github.com/whoskavic)

## 🙏 Acknowledgments

- TradingView for chart widgets
- Anthropic for Claude AI API
- FastAPI and React communities

---

⭐ Star this repo if you find it helpful!
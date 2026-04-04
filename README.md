# AI-Based Citizen Grievance Classification System

An end-to-end prototype that lets citizens submit text complaints in English or Indian regional languages. The system automatically classifies each complaint using NLP + Machine Learning, assigns it to the correct government department, and detects urgency via keyword/sentiment analysis.

---

## Architecture

```
├── backend/          Python FastAPI + SQLite + scikit-learn ML
└── frontend/         React (Vite) dashboard
```

---

## Features

| Feature | Details |
|---------|---------|
| **Submit complaint** | Web form; plain text, min 20 chars |
| **Multilingual support** | Auto-detects language (langdetect), translates to English (GoogleTranslator) before classification |
| **NLP preprocessing** | NLTK tokenisation · stopword removal · Porter stemming |
| **ML classifier** | TF-IDF + Logistic Regression (≈ 83 % accuracy on sample set); keyword fallback when no model is loaded |
| **Priority detection** | Keyword list + simple sentiment score → low / normal / high / urgent |
| **Department routing** | Each category maps to a department automatically |
| **REST API** | FastAPI, JWT auth, role-based access (citizen / admin / department\_officer) |
| **Dashboard** | Complaint list with filters (category, department, priority, status), pagination |
| **Admin panel** | Stats cards + Recharts PieChart & BarCharts + recent-complaints table |
| **Status tracking** | Admin/officer can update status: pending → in\_progress → resolved → closed |

---

## Quick Start

### 1 – Backend

```bash
cd backend
pip install -r requirements.txt

# Train the classifier (produces models/classifier.pkl + models/vectorizer.pkl)
python train_model.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs available at <http://localhost:8000/docs>

### 2 – Frontend

```bash
cd frontend
npm install
npm run dev        # starts on http://localhost:3000
```

The Vite dev server proxies `/api` requests to `localhost:8000`.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Register new user |
| POST | `/api/auth/login` | — | Login → JWT token |
| GET | `/api/auth/me` | Bearer | Current user info |
| POST | `/api/complaints/` | Optional | Submit & auto-classify complaint |
| GET | `/api/complaints/` | Optional | List complaints (filter by category/dept/priority/status) |
| GET | `/api/complaints/{id}` | Optional | Get single complaint |
| PATCH | `/api/complaints/{id}/status` | Admin/Officer | Update complaint status |
| GET | `/api/admin/stats` | Admin | Dashboard statistics |
| GET | `/api/admin/complaints` | Admin | All complaints (admin view) |

---

## Categories & Department Routing

| Category | Department |
|----------|-----------|
| electricity | Electricity Department |
| water\_supply | Water Supply Department |
| sanitation | Sanitation Department |
| roads | Roads & Infrastructure Department |
| public\_services | Public Services Department |

---

## ML Model

- **Algorithm**: Logistic Regression (scikit-learn) with TF-IDF vectoriser
- **Training data**: 60 labelled samples in `backend/sample_data.json` (12 per category)
- **Accuracy**: ~83 % on held-out test split
- **Fallback**: keyword-based classifier is used if no trained model is present
- **Upgrade path**: swap `LogisticRegression` for a BERT pipeline in `backend/app/ml/classifier.py`

---

## Roles

| Role | Capabilities |
|------|-------------|
| citizen | Submit complaints, view own complaints |
| department\_officer | View all complaints, update status |
| admin | Full access + admin dashboard |

To make a user an admin update the `role` column in the SQLite DB:

```python
# python3
from backend.app.database import SessionLocal
from backend.app.models import User
db = SessionLocal()
u = db.query(User).filter(User.username == "yourusername").first()
u.role = "admin"
db.commit()
```

---

## Sample Data

`backend/sample_data.json` contains 60 pre-labelled grievance texts (12 per category) used to train the classifier. Add more rows and re-run `python train_model.py` to retrain.

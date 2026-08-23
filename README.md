# Agentic-Travel Guide

An AI-powered travel planning and product discovery platform that generates personalized trip itineraries with real-time pricing, weather-aware scheduling, and smart product recommendations — all orchestrated by multi-agent LangGraph workflows.

---

## Features

### AI Trip Planner
- **Multi-agent pipeline** — Weather → Transport → Planner → Budget → Validator → Critic, orchestrated via LangGraph with automatic retry loops
- **Real-time web search** — Pulls live hotel, restaurant, and attraction prices using Tavily search
- **Weather-aware planning** — Fetches OpenWeatherMap forecasts and tailors activities + packing lists accordingly
- **Transport options** — Compares flights, trains, and buses with estimated prices and durations
- **Budget validation** — A dedicated critic agent audits the plan against your budget, retrying up to 3 times if violations are found
- **Plan history & ratings** — Save plans to Supabase and rate them (hotels, activities, budget accuracy) to improve future suggestions

### Smart Product Finder
- **Research → Analyze → Curate pipeline** — A separate LangGraph workflow that searches, scores, and filters products
- **Budget-constrained results** — Specify a max price and get curated recommendations within budget
- **Category filtering** — Narrow results by product category

### Authentication
- **Clerk integration** — Sign-in/sign-up with Clerk on the frontend, JWT verification on the backend
- **Protected routes** — All app pages require authentication

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)             │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │Dashboard │  │ TripPlanner │  │  ProductFinder   │   │
│  └──────────┘  └─────────────┘  └──────────────────┘   │
│          │             │                │               │
│          └─────────────┼────────────────┘               │
│                        │  Axios + React Query           │
│                    Clerk Auth                           │
└────────────────────────┼────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────┼────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                        │                                │
│  ┌─────────────────────┼──────────────────────────┐     │
│  │              LangGraph Agents                  │     │
│  │                                                │     │
│  │  Trip Planning Graph:                          │     │
│  │  Weather → Transport → Planner → Budget →      │     │
│  │  Validator → Critic ──┐                        │     │
│  │       ▲                │                       │     │
│  │       └── retry ◄──── rejected?                │     │
│  │                        │                       │     │
│  │                    Finalizer → Response         │     │
│  │                                                │     │
│  │  Product Search Graph:                         │     │
│  │  Researcher → Analyzer → Curator → Finalizer   │     │
│  └────────────────────────────────────────────────┘     │
│                        │                                │
│  ┌──────────┐  ┌───────┴──────┐  ┌─────────────────┐   │
│  │ Supabase │  │ Gemini 2.5   │  │ Tavily / OWM    │   │
│  │   (DB)   │  │  Flash (LLM) │  │  (Web Search)   │   │
│  └──────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, Zustand, React Query, React Router |
| **Auth** | Clerk (frontend SDK + backend JWT verification) |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI / Agents** | LangGraph, LangChain, Google Gemini 2.5 Flash |
| **Search** | Tavily API (web search for real-time pricing) |
| **Weather** | OpenWeatherMap API |
| **Database** | Supabase (PostgreSQL) |
| **Validation** | Pydantic (backend), TypeScript (frontend) |

---

## Project Structure

```
life-logistics-copilot/
├── backend/
│   ├── app/
│   │   ├── agents/             # LangGraph agent nodes & graphs
│   │   │   ├── graph.py        # Trip planning workflow (main graph)
│   │   │   ├── product_graph.py# Product search workflow
│   │   │   ├── planner.py      # Trip itinerary generation agent
│   │   │   ├── budget.py       # Budget estimation agent
│   │   │   ├── budget_validator.py # Budget compliance checker
│   │   │   ├── weather.py      # Weather data fetcher
│   │   │   ├── transport.py    # Transport options agent
│   │   │   ├── product_researcher.py  # Product web search
│   │   │   ├── product_analyzer.py    # Product scoring & analysis
│   │   │   ├── product_curator.py     # Product filtering & curation
│   │   │   ├── state.py        # Trip agent state definition
│   │   │   ├── product_state.py# Product agent state definition
│   │   │   └── tools.py        # Shared tool definitions
│   │   ├── api/                # FastAPI route handlers
│   │   │   ├── routes.py       # API router aggregator
│   │   │   ├── plan.py         # /api/plan endpoints
│   │   │   ├── product.py      # /api/product endpoints
│   │   │   └── user.py         # /api/user endpoints
│   │   ├── core/               # App configuration & utilities
│   │   │   ├── config.py       # Environment variable loader
│   │   │   ├── db.py           # Supabase client setup
│   │   │   ├── security.py     # Clerk JWT verification
│   │   │   └── slm_engine.py   # Custom SLM architecture (experimental)
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic request/response models
│   │   └── main.py             # FastAPI app entrypoint
│   ├── .env                    # Backend environment variables
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx   # Trip overview & history
│   │   │   ├── TripPlanner.tsx # Trip planning interface
│   │   │   ├── ProductFinder.tsx # Product search interface
│   │   │   └── Settings.tsx    # User preferences
│   │   ├── components/
│   │   │   ├── layout/         # App shell, navigation
│   │   │   └── ui/             # Reusable UI components
│   │   ├── api/                # Axios API client
│   │   ├── store/              # Zustand state management
│   │   ├── lib/                # Utility functions
│   │   ├── App.tsx             # Root component & routing
│   │   ├── main.tsx            # React entry point
│   │   └── index.css           # Global styles
│   ├── .env                    # Frontend environment variables
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
└── .gitignore
```

---

## Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **npm** (comes with Node.js)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/life-logistics-copilot.git
cd life-logistics-copilot
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `backend/.env` file with:

```env
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
CLERK_SECRET_KEY=<your-clerk-secret-key>
CLERK_PEM_PUBLIC_KEY=<your-clerk-pem-public-key>
GOOGLE_API_KEY=<your-google-ai-api-key>
TAVILY_API_KEY=<your-tavily-api-key>
OPENWEATHERMAP_API_KEY=<your-openweathermap-api-key>
```

Create a `frontend/.env` file with:

```env
VITE_CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>
VITE_API_URL=http://localhost:8000/api
```

### 4. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173** (frontend) and **http://localhost:8000** (backend API).

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/plan` | Generate a trip plan |
| `GET` | `/api/plan` | Fetch saved plans |
| `POST` | `/api/user` | User profile operations |
| `POST` | `/api/product` | Search for products |

---

## How the AI Agents Work

### Trip Planning Graph

The trip planner uses a **LangGraph StateGraph** with 7 nodes:

1. **Weather Node** — Fetches forecast data from OpenWeatherMap for the destination and trip dates
2. **Transport Node** — Searches for real transport options (flights, trains, buses) with pricing
3. **Planner Node** — Uses Gemini 2.5 Flash + Tavily web search to generate a detailed itinerary with real hotel names, restaurant names, and attraction prices
4. **Budget Node** — Estimates per-day costs
5. **Budget Validator** — Checks that total costs align with the user's budget limit and flags violations
6. **Critic Node** — Reviews validation results; rejects the plan (sending it back to Planner) if budget violations exist, up to 3 retries
7. **Finalizer** — Approves and returns the final plan

### Product Search Graph

A 4-node pipeline:

1. **Researcher** — Searches the web for products matching the query and budget
2. **Analyzer** — Scores and ranks results based on relevance and price
3. **Curator** — Filters and formats the top results
4. **Finalizer** — Returns the curated product list

---

## License

This project is for personal/educational use.

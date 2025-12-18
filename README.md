# 📨 Inbox Zero Agent

![Status](https://img.shields.io/badge/Status-Active-success)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20LangGraph%20%7C%20Llama3-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

**Inbox Zero Agent** is an autonomous AI-powered email assistant designed to declutter your inbox. It securely connects to Gmail, scans for unread messages, and uses the **Llama 3** LLM to draft context-aware, professional replies automatically.

The application features a high-performance **"Cyber-Aurora"** interface with a responsive glassmorphism design, ensuring a seamless experience across desktop and mobile.

---

## ✨ Features

- **🚀 Smart Automation:** Scans your inbox for unread emails and drafts replies instantly.
- **🧠 Advanced AI Brain:** Powered by **Llama 3 (via Groq)** for human-like understanding.
- **🔐 Enterprise Security:** Uses **OAuth 2.0** for Google authentication and **Supabase RLS** to protect user tokens.
- **⚡ Batch Processing:** intelligently processes emails in batches (default: 5) to optimize performance.
- **🎨 Cyber-Aurora UI:** A fully immersive, animated interface with floating data particles and glassmorphism effects.
- **📱 Mobile Ready:** Fully responsive design that adapts to any screen size.

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework:** React + TypeScript (Vite)
- **Styling:** CSS3 (Animations, Glassmorphism, Responsive Grid)
- **Animation:** Framer Motion
- **Icons:** Lucide React
- **HTTP Client:** Axios

### **Backend**
- **Framework:** FastAPI (Python)
- **AI Orchestration:** LangGraph & LangChain
- **LLM Provider:** Groq (Llama 3.3 70B Versatile)
- **Database:** Supabase (PostgreSQL)
- **Integration:** Gmail API Toolkit

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v16+)
- **Python** (v3.10+)
- **Supabase Account** (for database)
- **Groq API Key** (for AI models)
- **Google Cloud Console Credentials** (OAuth Client ID & Secret)

### 1. Clone the Repository
git clone [https://github.com/yourusername/inbox-zero-agent.git](https://github.com/yourusername/inbox-zero-agent.git)
cd inbox-zero-agent

2. Backend Setup
Navigate to the backend folder and set up the Python environment.
cd backend
python -m venv vvenv
# Windows:
vvenv\Scripts\activate
# Mac/Linux:
source vvenv/bin/activate
pip install -r requirements.txt

Create a .env file in the backend/ folder:


GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_supabase_postgres_connection_string


3. Frontend Setup
Open a new terminal and navigate to the frontend folder.
cd frontend
npm install
Create a .env file in the frontend/ folder:


VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id

🏃‍♂️ Running the App
1. Start the Backend Server:
# From the backend/ folder
python main.py

Server runs at: http://localhost:8000

2. Start the Frontend Interface:

# From the frontend/ folder
npm run dev
App runs at: http://localhost:5173

🗄️ Database Schema (Supabase)
Run this SQL in your Supabase SQL Editor to set up the necessary table:

create table users (
  email text primary key,
  access_token text not null,
  refresh_token text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table users enable row level security;


🛡️ Security Note
This project uses OAuth 2.0 to access Gmail. It requests minimal scopes (gmail.readonly and gmail.compose).

Tokens are stored securely in Supabase.

RLS (Row Level Security) prevents unauthorized database access.

The .gitignore file ensures sensitive keys are never committed to the repository.

🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request for any feature updates.

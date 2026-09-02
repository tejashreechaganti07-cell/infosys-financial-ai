**# 📊 Multi-Agent Financial Research System**

> An AI-powered financial research platform that leverages multiple specialized AI agents to analyze company financial documents, extract key insights, identify financial risks, compare companies, answer research queries, and generate analyst-style reports.

**---**

**## 📌 Project Overview**

The ****Multi-Agent Financial Research System**** is designed to simplify financial analysis for students, researchers, and analysts. The platform enables users to upload financial documents such as Annual Reports and 10-K filings, automatically analyze them using specialized AI agents, and generate structured financial insights with source-grounded responses.

The system follows a multi-agent architecture where each agent performs a dedicated task in the financial research workflow.

**---**

**## ✨ Key Features**

- 📄 Financial Document Upload

- 📑 Automatic Document Processing

- 📊 Financial Metrics Extraction

- 🚩 Red Flag & Risk Detection

- 📈 Company Comparison

- 💬 Conversational Financial Research

- 📋 AI Generated Research Reports

- 📂 Research Workspace Management

- 🔐 Secure User Authentication

**---**

**# 🤖 Multi-Agent Workflow**

```

Financial Document

```
    │

    ▼
```

Document Agent

```
    │

    ▼
```

Extraction Agent

```
    │

    ▼
```

Red Flag Agent

```
    │

    ▼
```

Comparison Agent

```
    │

    ▼
```

Research Agent

```
    │

    ▼
```

Report Agent

```
    │

    ▼
```

Research Report (PDF)

```

**---**

**# 🏗️ Tech Stack**

**## Frontend**

- React

- Vite

- Tailwind CSS

- React Router

- Axios

**## Backend**

- FastAPI

- Python

- JWT Authentication

**## Database**

- MongoDB Atlas

**## AI Framework**

- CrewAI

- OpenAI

- MongoDB Atlas Vector Search

**---**

**# 📂 Project Structure**

```

infosys-financial-ai

│

├── Frontend

│   ├── src

│   │   ├── components

│   │   ├── context

│   │   ├── hooks

│   │   ├── pages

│   │   ├── services

│   │   ├── App.jsx

│   │   ├── main.jsx

│   │   └── index.css

│   │

│   ├── index.html

│   ├── package.json

│   ├── vite.config.js

│   ├── tailwind.config.js

│   └── postcss.config.js

│

├── Backend

│   ├── app

│   │   ├── api

│   │   ├── core

│   │   ├── models

│   │   ├── schemas

│   │   ├── services

│   │   └── main.py

│   │

│   ├── requirements.txt

│   └── test_backend.py

│

└── README.md

```

---

# ⚙️ Installation

## Clone Repository

```bash

git clone <repository-url>

```

```bash

cd infosys-financial-ai

```

**---**

**## Frontend Setup**

Move to the frontend folder.

```bash

cd Frontend

```

Install dependencies.

```bash

npm install

```

Start the development server.

```bash

npm run dev

```

**---**

**## Backend Setup**

Move to the backend folder.

```bash

cd Backend

```

Create a virtual environment.

**### Windows**

```bash

python -m venv venv

```

```bash

venv\Scripts\activate

```

**### Linux / macOS**

```bash

python3 -m venv venv

```

```bash

source venv/bin/activate

```

Install dependencies.

```bash

pip install -r requirements.txt

```

Run the backend server.

```bash

uvicorn app.main:app --reload

```

**---**

**# 🔧 Environment Variables**

Create a `.env` file inside the Backend folder.

```env

MONGODB_URI=your_mongodb_connection_string

DATABASE_NAME=financial_research

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

```

**---**

**# 🧩 AI Agents**

**### 📄 Document Agent**

- Document Upload

- PDF Parsing

- Text Chunking

- Embedding Generation

- Vector Database Indexing

**### 📊 Extraction Agent**

- Financial Metrics Extraction

- Ratio Calculation

- Revenue & Profit Analysis

**### 🚩 Red Flag Agent**

- Risk Detection

- Debt Analysis

- Margin Analysis

- Financial Anomaly Detection

**### 📈 Comparison Agent**

- Cross Company Benchmarking

- Peer Comparison

- Performance Analysis

**### 💬 Research Agent**

- Financial Question Answering

- Multi-step Reasoning

- Source-based Responses

**### 📋 Report Agent**

- Executive Summary

- Key Financials

- Red Flags

- Company Comparison

- PDF Report Generation

**---**

**# 🚀 Current Development Status**

| Module | Status |
|---------|--------|
| Frontend Setup | ✅ Completed |
| Backend Setup | ✅ Completed |
| Project Structure | ✅ Completed |
| Authentication | 🚧 In Progress |
| Dashboard | 🚧 In Progress |
| Research Workspace | 🚧 In Progress |
| Document Upload | 🚧 In Progress |
| MongoDB Integration | 🚧 In Progress |
| Multi-Agent Workflow | ⏳ Planned |
| Report Generation | ⏳ Planned |

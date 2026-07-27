# 🚀 Firstsource POC – AI Incoming Request Processing Workflow

An **Agentic AI Proof of Concept (POC)** built as part of the **Firstsource Solutions AI Engineer Assessment**.

The application processes incoming customer requests using **Google Gemini AI** for intelligent analysis and a **deterministic workflow engine** for business decision-making. It demonstrates how Large Language Models (LLMs) can be integrated into enterprise workflows while ensuring reliability, transparency, and maintainability.

---

## 📌 Project Overview

The system is designed with a **two-layer architecture**:

### 🤖 AI Layer (Gemini)

Responsible for understanding customer requests by:

- Classifying request category
- Detecting urgency
- Extracting important entities
- Generating reasoning
- Producing a confidence score
- Drafting a customer response

---

### ⚙️ Workflow Layer (Python)

Responsible for deterministic business execution:

- Workflow routing
- Department assignment
- Human review decisions
- Business actions
- Logging
- SQLite persistence
- Dashboard analytics

This separation ensures that **AI performs reasoning**, while **Python performs business logic**, making the application reliable and production-friendly.

---

# 🏗️ Architecture

```text
                Customer Request
                       │
                       ▼
               Streamlit Interface
                       │
                       ▼
                Gemini AI Analysis
                       │
     ┌─────────────────┼──────────────────┐
     │                 │                  │
 Classification   Entity Extraction   Confidence Score
     │                 │                  │
     └─────────────────┼──────────────────┘
                       │
                       ▼
             Workflow Manager (Python)
                       │
        ┌──────────────┼───────────────┐
        │              │               │
 Complaint     Service Request    General Enquiry
        │              │               │
        └──────────────┼───────────────┘
                       │
                 Escalation Logic
                       │
                       ▼
               SQLite Database
                       │
                       ▼
         History & Analytics Dashboard
```

---

# ✨ Features

## AI Capabilities

- Google Gemini Flash Integration
- Customer Request Classification
- Urgency Detection
- Entity Extraction
- AI Reasoning
- Confidence Score
- Draft Response Generation

---

## Workflow Automation

- Complaint Workflow
- General Enquiry Workflow
- Service Request Workflow
- Escalation Workflow
- Human Review Trigger
- Department Routing
- SLA Tracking (Simulation)

---

## User Interface

Built using **Streamlit**

Includes:

- Home
- Request History
- Dashboard
- Configuration
- About Project

---

## Dashboard

Visual analytics include:

- Total Requests
- Complaint Count
- Service Requests
- General Enquiries
- Escalations
- Confidence Distribution
- Recent Requests
- Workflow Statistics

---

# 📂 Project Structure

```text
firstsource_poc/

├── app.py
├── README.md
├── requirements.txt
├── .env.example

├── config/
│   └── agent_config.py

├── core/
│   ├── batch_processor.py
│   ├── database.py
│   ├── gemini_client.py
│   ├── logger.py
│   ├── prompts.py
│   ├── schemas.py
│   └── workflow_manager.py

├── ui/

├── data/
│   └── sample_emails.csv
```

---

# 🛠️ Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.11+ |
| UI | Streamlit |
| AI Model | Google Gemini Flash |
| Validation | Pydantic |
| Database | SQLite |
| Configuration | python-dotenv |
| Parallel Processing | ThreadPoolExecutor |
| Logging | Python Logging |

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/AmanCh786/firstsourcedemolink.git

cd firstsourcedemolink
```

Create virtual environment

```bash
python -m venv .venv
```

Activate environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create environment file

```bash
cp .env.example .env
```

Add your Gemini API Key

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

The application will launch locally in your browser.

---

# ⚙️ Configuration

The application is fully configurable through **.env**.

## Gemini Configuration

| Variable | Description |
|-----------|-------------|
| GEMINI_MODEL | Gemini model name |
| GEMINI_TEMPERATURE | Temperature |
| GEMINI_TOP_P | Top P |
| GEMINI_MAX_TOKENS | Maximum Output Tokens |
| CONFIDENCE_THRESHOLD | Human Review Threshold |

---

## Batch Configuration

| Variable | Description |
|-----------|-------------|
| ENABLE_BATCH_PROCESSING | Enable CSV Processing |
| BATCH_SIZE | Requests per Batch |
| MAX_PARALLEL_WORKERS | Parallel Workers |
| MAX_BATCH_REQUESTS | Maximum CSV Size |

---

# 🔄 Workflow

## Single Request Flow

```text
Customer Request
        │
        ▼
 Gemini Analysis
        │
        ▼
 JSON Validation
        │
        ▼
 Workflow Manager
        │
        ▼
 Business Actions
        │
        ▼
 SQLite Logging
        │
        ▼
 Dashboard
```

---

## Batch Processing Flow

```text
CSV Upload
      │
      ▼
Split into Batches
      │
      ▼
Parallel Gemini Calls
      │
      ▼
Workflow Execution
      │
      ▼
Database
      │
      ▼
Dashboard
```

---

# 📌 Workflow Types

## Complaint

- Create Priority Case
- Assign Billing Team
- Two-hour Follow-up
- Generate Acknowledgement

---

## General Enquiry

- Categorise Query
- Generate AI Response
- Resolve Automatically
- Log Request

---

## Service Request

- Validate Details
- Route to Operations
- Generate Confirmation
- Start SLA Timer

---

## Escalation

- Assign Senior Manager
- Human Review
- Priority Notification
- Pause Auto Resolution

---

# 📊 Sample Scenarios

### Complaint

Duplicate billing request

↓

High Priority

↓

Billing Team

↓

Priority Case Created

---

### General Enquiry

Broadband plan question

↓

General Enquiry

↓

Knowledge Response Generated

↓

Resolved

---

### Service Request

New broadband connection

↓

Operations

↓

Confirmation Generated

↓

SLA Started

---

### Escalation

Repeated unresolved complaint

↓

Critical

↓

Senior Manager

↓

Human Review

---

# 🧠 Design Principles

- Separation of AI and Business Logic
- Deterministic Workflow Routing
- Schema Validation using Pydantic
- Confidence-based Human Review
- Modular Architecture
- Configurable Environment
- Scalable Batch Processing
- Production-oriented Design

---

# 🔮 Future Enhancements

- Gmail API Integration
- Real Email Dispatch
- REST API
- Docker Support
- Authentication
- Multi-user Access
- Cloud Database
- Unit & Integration Tests
- Kubernetes Deployment

---

# 📷 Application Screenshots

https://firstsourcedemolink-wymqbpxk6fjexterx6jrws.streamlit.app/

```
Home Page

Dashboard

Request History

Configuration

Batch Processing
```

---

# 👨‍💻 Author

**Aman Chauhan**

B.Tech Computer Science & Engineering

Vellore Institute of Technology (VIT), Vellore

GitHub: https://github.com/AmanCh786

LinkedIn: https://linkedin.com/in/aman-chauhan-128552256

---

# 📄 License

This project was developed as part of the **Firstsource Solutions AI Engineer Technical Assessment** and is intended for educational and demonstration purposes.

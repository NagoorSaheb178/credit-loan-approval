# Credit Approval System

## 📌 Overview

This project implements a Credit Approval System using Django 4+, Django Rest Framework, PostgreSQL, Celery, and Docker.

The system evaluates loan eligibility based on historical loan data and predefined business rules such as credit scoring, interest slabs, and EMI burden constraints.

The entire application is fully dockerized and runs using a single Docker Compose command.

---

## 🏗 Tech Stack

- Python 3.11
- Django 4+
- Django Rest Framework
- PostgreSQL
- Redis
- Celery (Background Worker)
- Docker & Docker Compose

---

## 🚀 How to Run

Ensure Docker is installed.

### Start Application

```bash
docker compose up --build
```

After successful startup:

- Server runs at:

```
http://localhost:8000/
```

- API base URL:

```
http://localhost:8000/api/
```

---

## 🛑 Stop Application

```bash
docker compose down
```

To remove volumes (fresh start):

```bash
docker compose down -v
```

---

## 📂 Data Initialization

On first startup, the following Excel files are ingested into the database using a Celery background task:

- `customer_data.xlsx`
- `loan_data.xlsx`

The ingestion process is idempotent and prevents duplicate entries on restart.

---

## 🗄 Database Configuration (Docker)

```
Database: credit_db
User: credit_user
Password: credit_pass
Host: db
Port: 5432
```

If connecting via pgAdmin (outside Docker):

```
Host: localhost
Port: 5432
Username: credit_user
Password: credit_pass
Database: credit_db
```

---

# 📡 API Endpoints

---

## 1️⃣ Register Customer

**POST** `/api/register/`

### Request Body

```json
{
  "first_name": "Ravi",
  "last_name": "Kumar",
  "age": 25,
  "monthly_income": 50000,
  "phone_number": "9876543210"
}
```

### Business Logic

```
approved_limit = 36 × monthly_income
```

Rounded to nearest lakh.

---

## 2️⃣ Check Loan Eligibility

**POST** `/api/check-eligibility/`

### Request Body

```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}
```

### Rules Implemented

- Credit score calculation (0–100)
- Slab-based interest approval
- Interest rate correction if below slab
- EMI burden rule (≤ 50% of salary)
- Debt > approved limit → credit_score = 0

---

## 3️⃣ Create Loan

**POST** `/api/create-loan/`

Creates loan only if eligibility conditions are satisfied.

Returns loan ID if approved, otherwise returns rejection message.

---

## 4️⃣ View Loan Details

**GET** `/api/view-loan/<loan_id>/`

Returns:
- Loan details
- Associated customer information

---

## 5️⃣ View All Loans of Customer

**GET** `/api/view-loans/<customer_id>/`

Returns all active loans and remaining EMIs.

---

# 📊 Credit Score Calculation

Credit score (0–100) is calculated using:

- 40% → On-time EMI repayment ratio
- 20% → Loan frequency penalty
- 20% → Debt utilization ratio
- 20% → Base score

If total outstanding loan amount exceeds approved limit:

```
credit_score = 0
```

---

# 💰 EMI Formula (Compound Interest)

Monthly interest rate:

```
r = annual_rate / (12 × 100)
```

EMI calculation:

```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)
```

Where:

- P = Loan Amount  
- r = Monthly Interest Rate  
- n = Tenure (months)

---

# 📌 Loan Approval Slabs

| Credit Score | Approval Rule |
|--------------|--------------|
| > 50 | Loan Approved |
| 50–30 | Approved if interest ≥ 12% |
| 30–10 | Approved if interest ≥ 16% |
| < 10 | Loan Rejected |

Additional rule:

- If total EMIs exceed 50% of monthly income → Loan Rejected

If interest rate does not meet slab requirement, a `corrected_interest_rate` is returned in response.

---

# 🧪 API Testing Examples (HTTP)

Base URL:

```
http://localhost:8000/api/
```

---

## Register Customer

```bash
curl -X POST http://localhost:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
  "first_name": "Ravi",
  "last_name": "Kumar",
  "age": 25,
  "monthly_income": 50000,
  "phone_number": "9876543210"
}'
```

---

## Check Eligibility

```bash
curl -X POST http://localhost:8000/api/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}'
```

---

## Create Loan

```bash
curl -X POST http://localhost:8000/api/create-loan/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 12,
  "tenure": 12
}'
```

---

## View Loan

```bash
curl http://localhost:8000/api/view-loan/1/
```

---

## View All Loans

```bash
curl http://localhost:8000/api/view-loans/1/
```

---

# 🧱 Architecture

- `models.py` → Database schema
- `serializers.py` → Input validation
- `services.py` → Business logic
- `tasks.py` → Background Excel ingestion
- `views.py` → API handling
- `docker-compose.yml` → Container orchestration

---

# 🔐 Error Handling

- 400 → Invalid input
- 404 → Resource not found
- Idempotent ingestion
- Atomic loan creation
- Proper validation via serializers

---

# 🎯 Conclusion

This system demonstrates:

- REST API development using DRF
- Financial computation using compound interest
- Background processing using Celery
- Business rule enforcement
- Dockerized backend architecture
- Clean separation of concerns

---

# Credit Approval System (Professional Version)

## Run
docker compose up --build

## Architecture
- Models: Data layer
- Serializers: Input validation
- Services: Business logic (EMI, Credit Score, Eligibility)
- Tasks: Background Excel ingestion via Celery
- Fully Dockerized stack

## Credit Score (0–100)
40% On-time repayment ratio
20% Loan frequency penalty
20% Debt utilization
20% Base score
If total debt > approved limit → score = 0

## EMI Formula
EMI = P*r*(1+r)^n / ((1+r)^n -1)
r = annual_rate / (12*100)

## Rules Implemented
- Slab-based approval
- Interest correction
- 50% EMI burden rejection

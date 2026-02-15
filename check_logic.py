import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_response(res, label):
    print(f"\n--- {label} ---")
    try:
        print(json.dumps(res.json(), indent=2))
    except:
        print(res.text)

# 1. Register a new customer (High Income)
data_high = {
    "first_name": "Rich",
    "last_name": "Guy",
    "age": 35,
    "monthly_income": 150000,
    "phone_number": "1234567890"
}
res = requests.post(f"{BASE_URL}/register/", json=data_high)
print_response(res, "Register High Income User")
cust_high_id = res.json().get('customer_id')

# 2. Check Eligibility (Should start with default score 75 -> Approved)
if cust_high_id:
    data = {
        "customer_id": cust_high_id,
        "loan_amount": 500000,
        "interest_rate": 10.0,
        "tenure": 12
    }
    res = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_response(res, "Check Eligibility (New User)")

# 3. Register a new customer (Low Income)
data_low = {
    "first_name": "Broke",
    "last_name": "Med",
    "age": 25,
    "monthly_income": 20000,
    "phone_number": "0987654321"
}
res = requests.post(f"{BASE_URL}/register/", json=data_low)
print_response(res, "Register Low Income User")
cust_low_id = res.json().get('customer_id')

# 4. Check Eligibility (High EMI request -> Should Fail on Income Ratio)
if cust_low_id:
    data = {
        "customer_id": cust_low_id,
        "loan_amount": 500000, 
        "interest_rate": 12.0,
        "tenure": 12
    }
    # EMI for 5L @ 12% for 12m is ~44k, which is > 50% of 20k income.
    res = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_response(res, "Check Eligibility (High EMI Ratio - Expect Failure)")

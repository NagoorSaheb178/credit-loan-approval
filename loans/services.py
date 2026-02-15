from datetime import date
from django.db.models import Sum
from .models import Loan, Customer

def calculate_emi(P, annual_rate, tenure):
    r = annual_rate / (12 * 100)
    if r == 0:
        return round(P / tenure, 2)
    emi = P * r * (1 + r)**tenure / ((1 + r)**tenure - 1)
    return round(emi, 2)

def calculate_credit_score(customer, loans):
    if not loans:
        return 75  # Default score for new customers? Or calculate based on salary/other metrics? Assignment implies default handling.
    
    total_loans = len(loans)
    total_debt = sum(l.loan_amount for l in loans if l.status == 'ACTIVE') # Only active loans count towards debt cap? Or all historical loans? "Sum of current loans" implies active.
    
    # Check 1: If sum of current loans > approved limit, score = 0
    if total_debt > customer.approved_limit:
        return 0

    # Component 1: Past Loans paid on time (Weighted 40%)
    total_tenure = sum(l.tenure for l in loans)
    total_paid_on_time = sum(l.emis_paid_on_time for l in loans)
    ratio_paid = (total_paid_on_time / total_tenure) if total_tenure > 0 else 1
    score_history = ratio_paid * 40 # Max 40 points

    # Component 2: No of loans taken in past (Weighted 20%)
    # Logic: More loans is good or bad? Usually moderate is good. Let's assume > 10 is risky?
    # Simple logic: 20 points, minus 2 for every loan.
    score_count = max(0, 20 - (total_loans * 2))

    # Component 3: Loan activity in current year (Weighted 20%)
    current_year = date.today().year
    loans_this_year = sum(1 for l in loans if l.start_date.year == current_year)
    # Logic: Fewer loans this year is better? 
    # Let's say: 20 points - (5 points per loan this year)
    score_activity = max(0, 20 - (loans_this_year * 5))

    # Component 4: Loan approved volume (Weighted 20%)
    # Logic: If total historical approved amount is close to limit, maybe risky?
    # Let's calculate based on total_debt / approved_limit
    debt_ratio = total_debt / customer.approved_limit if customer.approved_limit > 0 else 1
    score_volume = max(0, 20 - (debt_ratio * 20))

    # Total Score
    final_score = score_history + score_count + score_activity + score_volume
    return int(min(100, max(0, final_score)))

def check_eligibility(customer, loan_amount, interest_rate, tenure):
    # Fetch customer's historical loans
    loans = list(Loan.objects.filter(customer=customer))
    
    # Calculate Credit Score
    credit_score = calculate_credit_score(customer, loans)
    
    # Calculate EMI for requested loan
    requested_emi = calculate_emi(loan_amount, interest_rate, tenure)
    
    # Determine Approval and Interest Rate Correction
    approved = False
    corrected_interest_rate = interest_rate
    
    if credit_score > 50:
        approved = True
        corrected_interest_rate = interest_rate # Start with requested
    elif 50 >= credit_score > 30:
        if interest_rate >= 12:
            approved = True
            corrected_interest_rate = interest_rate
        else:
            approved = True # Assignment says "approve loans with interest rate > 12%", confusing if simple reject or correct.
            # "If the interest rate does not match as per credit limit , correct the interest rate in the response"
            # So we approve but correct the rate.
            corrected_interest_rate = 12.0
    elif 30 >= credit_score > 10:
        if interest_rate >= 16:
            approved = True
            corrected_interest_rate = interest_rate
        else:
            approved = True
            corrected_interest_rate = 16.0
    elif 10 >= credit_score:
        approved = False # Don't approve any loans
    
    # Check EMI vs Salary Cap (Sum of all CURRENT EMIs > 50% monthly salary)
    # A loan is "current" if it's active and hasn't reached its end date (if defined)
    active_loans = []
    for l in loans:
        if l.status == 'ACTIVE':
            if l.end_date:
                if l.end_date >= date.today():
                    active_loans.append(l)
            else:
                active_loans.append(l)
    
    current_emis = sum(l.monthly_installment for l in active_loans)
    
    if (current_emis + requested_emi) > (0.5 * customer.monthly_income):
        approved = False # Strict rejection
        
    # Recalculate EMI if interest rate changed (only if approved, or for display purposes)
    final_emi = calculate_emi(loan_amount, corrected_interest_rate, tenure)
            
    return approved, corrected_interest_rate, final_emi, credit_score

def register_customer(data):
    approved_limit = round((36 * data['monthly_income']) / 100000) * 100000 # Rounded to nearest lakh
    customer = Customer.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        phone_number=data['phone_number'],
        monthly_income=data['monthly_income'],
        approved_limit=approved_limit
    )
    return customer
    
def process_loan_application(customer_id, loan_amount, interest_rate, tenure):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return None, "Customer not found"
        
    approved, corrected_rate, emi, _ = check_eligibility(customer, loan_amount, interest_rate, tenure)
    
    if not approved:
        return None, "Loan not approved based on eligibility criteria"
        
    from dateutil.relativedelta import relativedelta
    start_date = date.today()
    end_date = start_date + relativedelta(months=tenure)

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_rate,
        monthly_installment=emi,
        start_date=start_date,
        end_date=end_date,
        status='ACTIVE'
    )
    return loan, "Loan approved"

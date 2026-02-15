from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan, Customer
from .serializers import RegisterSerializer, LoanRequestSerializer
from .services import check_eligibility, register_customer, process_loan_application

@api_view(['GET'])
def api_root(request):
    return Response({
        "register": "/register/",
        "check_eligibility": "/check-eligibility/",
        "create_loan": "/create-loan/",
        "view_loan": "/view-loan/<loan_id>/",
        "view_loans": "/view-loans/<customer_id>/"
    })

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    customer = register_customer(serializer.validated_data)
    
    return Response({
        "customer_id": customer.id,
        "name": f"{customer.first_name} {customer.last_name}",
        "age": customer.age,
        "monthly_income": customer.monthly_income,
        "approved_limit": customer.approved_limit,
        "phone_number": customer.phone_number
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def check_eligibility_view(request):
    serializer = LoanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    data = serializer.validated_data
    
    try:
        customer = Customer.objects.get(id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    approved, corrected_rate, emi, _ = check_eligibility(
        customer, data['loan_amount'], data['interest_rate'], data['tenure']
    )

    return Response({
        "customer_id": customer.id,
        "approval": approved,
        "interest_rate": data['interest_rate'],
        "corrected_interest_rate": corrected_rate,
        "tenure": data['tenure'],
        "monthly_installment": emi
    })

@api_view(['POST'])
def create_loan(request):
    serializer = LoanRequestSerializer(data=request.data)
    if not serializer.is_valid():
         return Response(serializer.errors, status=400)
    data = serializer.validated_data
    
    loan, message = process_loan_application(
        data['customer_id'], data['loan_amount'], data['interest_rate'], data['tenure']
    )
    
    if not loan:
        return Response({
            "loan_id": None,
            "customer_id": data['customer_id'],
            "loan_approved": False,
            "message": message,
            "monthly_installment": 0 # Provide default or calculated? Assignment says "monthly_installment" in response. 
            # Ideally we'd calculate it even if rejected for display, but service returns None. 
            # Let's keep it simple as per spec "message" is key.
        })

    return Response({
        "loan_id": loan.id,
        "customer_id": loan.customer.id,
        "loan_approved": True,
        "message": message,
        "monthly_installment": loan.monthly_installment
    }, status=201)

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=404)
    return Response({
        "loan_id": loan.id,
        "customer": {
            "id": loan.customer.id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure
    })

@api_view(['GET'])
def view_loans(request, customer_id):
    loans = Loan.objects.filter(customer_id=customer_id, status='ACTIVE')
    result = []
    for loan in loans:
        result.append({
            "loan_id": loan.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time
        })
    return Response(result)

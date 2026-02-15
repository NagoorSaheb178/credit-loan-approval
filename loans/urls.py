from django.urls import path
from .views import register, check_eligibility_view, create_loan, view_loan, view_loans, api_root
urlpatterns = [
    path('', api_root),
    path('register/', register),
    path('check-eligibility/', check_eligibility_view),
    path('create-loan/', create_loan),
    path('view-loan/<int:loan_id>/', view_loan),
    path('view-loans/<int:customer_id>/', view_loans),
]

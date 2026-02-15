from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "Credit Approval System API is running. Go to /api/ for endpoints."})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('loans.urls')),
]

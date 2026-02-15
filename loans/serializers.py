from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.FloatField(min_value=0)
    phone_number = serializers.CharField()

class LoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=1)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)

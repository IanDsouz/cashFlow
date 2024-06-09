from rest_framework import generics
from rest_framework.response import Response
from ..models import Income, Expense
from ..serializers import IncomeSerializer, ExpenseSerializer
from rest_framework.decorators import api_view

# Income APIs

class IncomeListAPIView(generics.ListAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeDetailAPIView(generics.RetrieveAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeCreateAPIView(generics.CreateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeUpdateAPIView(generics.UpdateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeDeleteAPIView(generics.DestroyAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

# Expense APIs

class ExpenseListAPIView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseDetailAPIView(generics.RetrieveAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseCreateAPIView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseUpdateAPIView(generics.UpdateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseDeleteAPIView(generics.DestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

# Additional APIs

@api_view(['GET'])
def get_monthly_income_total(request):
    # Your logic to calculate monthly income total
    return Response({'monthly_income_total': 1000.00})  # Replace with actual total

@api_view(['GET'])
def get_monthly_expense_total(request):
    # Your logic to calculate monthly expense total
    return Response({'monthly_expense_total': 500.00})  # Replace with actual total

@api_view(['GET'])
def get_yearly_income_total(request):
    # Your logic to calculate yearly income total
    return Response({'yearly_income_total': 12000.00})  # Replace with actual total

@api_view(['GET'])
def get_yearly_expense_total(request):
    # Your logic to calculate yearly expense total
    return Response({'yearly_expense_total': 6000.00})
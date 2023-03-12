from rest_framework import serializers
from .models import User, Budget, Category, Account, Income, Tag, Expense


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'



class ExpenseSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    account = AccountSerializer(many=False, read_only=True)

    class Meta:
        model = Expense
        fields = ('id', 'date', 'amount', 'tag', 'category', 'payment_method', 'account', 'user')
        depth = 1



class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('id', 'start_balance', 'end_balance')


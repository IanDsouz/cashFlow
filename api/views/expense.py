from rest_framework import status
from django.core import serializers as serializers_core
from django.http import HttpResponse
from rest_framework import serializers,viewsets
from django.http import JsonResponse
from django.db.models import Sum, Case, When, Value, IntegerField, Q, F, ExpressionWrapper, fields, FloatField
from rest_framework import generics, permissions
from  ..models import Expense, Budget, Category, Tag, Account, User
from ..serializers import UserSerializer, ExpenseSerializer, BudgetSerializer, CategorySerializer, ExpenseDisplaySerializer, TagSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework import status
import csv
import io
import re
import datetime
from collections import Counter
import io, csv, pandas as pd
from django.db import connection
from django.db.models.functions import Coalesce
import calendar 
from django.db.models.functions import ExtractMonth
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from django.db.models.functions import ExtractYear
from django.core.paginator import Paginator

class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self, request):
          
          try:
               refresh_token = request.data["refresh_token"]
               print(refresh_token)
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response(status=status.HTTP_400_BAD_REQUEST)
            

class ExpenseCreateAPIView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def generate_transaction_id(self):
        """Generate a unique transaction ID based on timestamp."""
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return f'TRAN-{timestamp}'

    def post(self, request, *args, **kwargs):
        # Get the data from the request
        amount = request.data.get('amount')
        description = request.data.get('description')
        category_id = request.data.get('category')
        date = request.data.get('date')
        tag_id = request.data.get('tag')
        notes = request.data.get('notes', '')
        recurring = request.data.get('recurring', False)
        payment_method = request.data.get('payment_method', 'Card')  # Default to 'Card'
        user_id = request.data.get('user', 1)  # Default user ID is Ian (1)

        if not amount or not category_id or not date or not tag_id:
            return JsonResponse(
                {'error': 'Amount, Category, Date, and Tag are required fields.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique transaction ID
        transaction_id = self.generate_transaction_id()

        # Get the category and tag objects
        category = get_object_or_404(Category, pk=category_id)
        tag = get_object_or_404(Tag, pk=tag_id)

        # Get the user and account objects (assuming default user is Ian, and default account is 1)
        user = get_object_or_404(User, pk=user_id)
        account = get_object_or_404(Account, pk=1)  # Assuming account ID 1 is default

        # Parse the date
        try:
            parsed_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()  # Assuming 'YYYY-MM-DD' format
        except ValueError:
            return JsonResponse(
                {'error': 'Invalid date format. Please use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare the expense data to be saved
        expense_data = {
            'description' : description,
            'transaction_id': transaction_id,
            'amount': amount,
            'category': category.id,
            'date': parsed_date,
            'tag': tag.id,
            'notes': notes,
            'recurring': recurring,
            'next_occurrence': None,  # This can be set later if recurring is True
            'payment_method': payment_method,
            'account': account.id,
            'user': user.id,
            'statement_text': tag.raw_description if tag else '',  # Assuming you want a description based on the tag
        }

        # Save the expense
        serializer = self.get_serializer(data=expense_data)
        if serializer.is_valid():
            serializer.save()  # Save the expense record to the database
            return JsonResponse(
                {'message': 'Expense created successfully!',
                 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class ExpenseByCategoryAPIView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')  # Extract category_id from URL
        expenses = self.queryset.filter(category_id=category_id)

        if not expenses:
            return JsonResponse(
                {'error': 'No expenses found for this category.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(expenses, many=True)
        return JsonResponse(
            {'message': 'Expenses by category retrieved successfully!', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

class ExpenseDeleteAPIView(generics.DestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = 'id'  # Use transaction_id as the lookup field

    def delete(self, request, *args, **kwargs):
        expense = self.get_object()  # Retrieve the expense object based on transaction_id
        expense.delete()  # Delete the expense
        return JsonResponse(
            {'message': 'Expense deleted successfully!'},
            status=status.HTTP_204_NO_CONTENT
        )

class ExpenseUpdateAPIView(generics.UpdateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = 'id'  # Use transaction_id as the lookup field

    def put(self, request, *args, **kwargs):
        expense = self.get_object()  # Retrieve the expense object based on transaction_id
        data = request.data

        # Optionally, you can validate and preprocess the data if needed
        data['id'] = expense.id  # Ensure the transaction_id stays the same

        # Update the expense
        serializer = self.get_serializer(expense, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {'message': 'Expense updated successfully!', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return JsonResponse(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, *args, **kwargs):
        expense = self.get_object()  # Retrieve the expense object based on transaction_id
        data = request.data

        # Optionally, you can validate and preprocess the data if needed
        data['transaction_id'] = expense.transaction_id  # Ensure the transaction_id stays the same

        # Update the expense partially
        serializer = self.get_serializer(expense, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {'message': 'Expense partially updated successfully!', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return JsonResponse(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class ExpenseRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = 'transaction_id'  # Use transaction_id as the lookup field

    def get(self, request, *args, **kwargs):
        expense = self.get_object()  # Retrieve the expense based on transaction_id
        serializer = self.get_serializer(expense)
        return JsonResponse(
            {'message': 'Expense retrieved successfully!', 'data': serializer.data},
            status=status.HTTP_200_OK
        )


class ExpenseUploadCreateAPIView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def post(self, request, *args, **kwargs):
        corrected_expenses = request.data.get('expenses')  # Corrected expenses with resolved tags

        if not corrected_expenses:
            return JsonResponse(
                {'error': 'No expenses data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=corrected_expenses, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {'message': 'Expenses created successfully!',
                 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class ExpenseCheckTagsAPIView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_generalized_tag(self, description):
        # Define patterns for Amazon transactions
        amazon_patterns = [
            r"AMZNMKTPLACE",    
            r"AMAZON.CO.UK",     
            r"AMAZON\s*[A-Z]*"   
        ]

        # Check if any of the patterns match the description
        for pattern in amazon_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return get_object_or_404(Tag, pk=213)
        return None

    def process_csv_file(self, file):
        expenses = []
        tags_found_count = 0
        tags_not_found_count = 0
        descriptions = []

        try:
            df = pd.read_csv(file)
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty or in an unsupported format.")

        for index, row in df.iterrows():
            date_str = row['Date']
            description = row['Description']
            amount_str = row['Amount']
            reference = row['Reference']

            try:
                amount = float(amount_str)
            except ValueError:
                raise ValueError(f"Invalid amount value: {amount_str}")

            if amount > 0:
                date_format = '%d/%m/%Y'
                try:
                    parsed_date = datetime.datetime.strptime(date_str, date_format).date()
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_str}")

                description_text = description.split() if 'Description' in df.columns else []
                filtered_words = [word for word in description_text if len(word) >= 3]
                if filtered_words:
                    description_text = filtered_words[0]

                tag = self.get_generalized_tag(description)

                if not tag:
                    tag = Tag.objects.filter(raw_description__istartswith=description_text).first()

                account = get_object_or_404(Account, pk=1)
                user = get_object_or_404(User, pk=1)

                if tag is None:
                    category = get_object_or_404(Category, pk=6)
                    tag = get_object_or_404(Tag, pk=70)
                    tags_not_found_count += 1
                    descriptions.append(description_text)
                else:
                    tags_found_count += 1
                    tag_id = tag.id if tag else None
                    category = tag.category

                expense = {
                    'transaction_id': reference.strip("'"),
                    'amount': amount,
                    'category': category.id, 
                    'date': parsed_date,
                    'tag': tag.id,
                    'notes': '',
                    'description': description,
                    'recurring': False,
                    'next_occurrence': None,
                    'payment_method': "Card",
                    'account': account.id,
                    'user': user.id,
                    'statement_text': description_text
                }
                expenses.append(expense)

        process_data = {
            'expenses': expenses,
            'tags_not_found_count': tags_not_found_count,
            'descriptions': descriptions
        }

        return process_data

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return JsonResponse(
                {'error': 'Missing file'},
                status=status.HTTP_400_BAD_REQUEST
            )

        process_data = self.process_csv_file(file)

        return JsonResponse(
            {
                'warning': 'Some tags were not found.' if process_data['tags_not_found_count'] > 0 else 'No tags missing.',
                'tags_not_found_count': process_data['tags_not_found_count'],
                'descriptions': process_data['descriptions'],
                'expenses': process_data['expenses']
            },
            status=status.HTTP_206_PARTIAL_CONTENT if process_data['tags_not_found_count'] > 0 else status.HTTP_200_OK
        )

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

               
    def get_generalized_tag(self, description):
        # Define patterns for Amazon transactions
        amazon_patterns = [
            r"AMZNMKTPLACE",    # Matches "AMZNMKTPLACE"
            r"AMAZON.CO.UK",     # Matches "AMAZON.CO.UK"
            r"AMAZON\s*[A-Z]*"   # Matches "AMAZON" followed by any characters
        ]

        # Check if any of the patterns match the description
        for pattern in amazon_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                # Return the specific tag with ID 213 for all Amazon transactions
                return get_object_or_404(Tag, pk=213)

        # If no pattern matches, return None
        return None

    def process_csv_file(self, file):
        expenses = []
        tags_found_count = 0
        tags_not_found_count = 0
        descriptions = []

        try:
            df = pd.read_csv(file)
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty or in an unsupported format.")

        for index, row in df.iterrows():
            date_str = row['Date']
            description = row['Description']
            amount_str = row['Amount']
            reference = row['Reference']

            try:
                amount = float(amount_str)
            except ValueError:
                raise ValueError(f"Invalid amount value: {amount_str}")

            if amount >0:
                date_format = '%d/%m/%Y'
                try:
                    parsed_date = datetime.datetime.strptime(date_str, date_format).date()
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_str}")

                try:
                    category_name = False
                    tag_name = False
                    description_text = description.split() if 'Description' in df.columns else []
                    filtered_words = [word for word in description_text if len(word) >= 3]

                    if filtered_words:
                        description_text = filtered_words[0]

                    tag = self.get_generalized_tag(description)

                    # If no generalized tag found, try finding tag by description
                    if not tag:
                        tag = Tag.objects.filter(raw_description__istartswith=description_text).first()

                    account = get_object_or_404(Account, pk=1)
                    user = get_object_or_404(User, pk=1)

                    if tag is None:
                        category = get_object_or_404(Category, pk=6)
                        tag = get_object_or_404(Tag, pk=70)
                        tags_not_found_count += 1
                        descriptions.append(description_text)
                    else:
                        tags_found_count += 1
                        tag_id = tag.id if tag else None
                        category = tag.category

                except Tag.DoesNotExist:
                    category = None
                    recurring = False
                expense = {
                    'transaction_id': reference.strip("'"),
                    'amount': amount,
                    'category': category.id, 
                    'date': parsed_date,
                    'tag': tag.id,
                    'notes': '',
                    'description': description,
                    'recurring': False,
                    'next_occurrence': None,
                    'payment_method': "Card",
                    'account': account.id,
                    'user': user.id,
                    'statement_text': description_text
                }
                expenses.append(expense)

        print('tags_found_count',tags_found_count)
        print('tags_not_found_count',tags_not_found_count)
        description_counts = Counter(descriptions)
        for description, count in description_counts.items():
            print(f"{description}: {count}")

        process_data = {}    

        process_data['expenses'] = expenses
        process_data['tags_not_found_count'] = tags_not_found_count
        process_data['descriptions'] = descriptions

        return process_data

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file :
            return JsonResponse(
                {'error': 'Missing file or account name'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process the CSV file and create expenses
        process_data = self.process_csv_file(file)

        if process_data['tags_not_found_count'] > 0:
            return JsonResponse(
            {
                'warning': 'Some tags were not found.',
                'tags_not_found_count': process_data['tags_not_found_count'],
                'descriptions': process_data['descriptions'],
                'expenses': process_data['expenses']
            },
            status=status.HTTP_206_PARTIAL_CONTENT  # Use 206 for partial success
        )

        serializer = self.get_serializer(data=process_data['expenses'], many=True)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse(
                {'message': 'Expenses created successfully',
                'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

def expense_summary(request, year, month):
    queryset = Expense.objects.filter(date__year=year, date__month=month, is_saving=False)
    serializer = ExpenseDisplaySerializer(queryset, many=True)
    categories = Category.objects.all()
    expenses = Expense.objects.filter(date__year=year, date__month=month).values('category__name').annotate(total=Sum('amount'))
    total_expense = round(sum(float(expense['amount']) for expense in serializer.data), 2)

    category_expenses = []
    planned_budget = 0
    for category in categories:
        expense = next((x for x in expenses if x['category__name'] == category.name), None)
        if expense:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            total = float(expense['total'])
            planned_budget = planned_budget + round(budget.start_balance, 2)

            expenses_list = ExpenseSerializer(
                            Expense.objects.filter(date__year=year, date__month=month, category=category),
                            many=True,
                            context={'request': request}  # Pass the request context to the serializer
                        ).data

            for expense_item in expenses_list:
                expense_item['tag'] = TagSerializer(
                    Tag.objects.get(id=expense_item['tag']),  # Fetch the Tag object by ID
                    context={'request': request}  # Pass the request context to the serializer
                ).data

            category_expenses.append({
            'name': category.name,
            'total': round(total, 2),
            'planned_expense': planned_expense,
            'expenses': expenses_list
        })
        else:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({
                'name': category.name,
                'total': 0,
                'planned_expense': planned_expense,
                'expenses': list(Expense.objects.filter(date__year=year, date__month=month, category=category).values())
            })
    return JsonResponse({'expenses': category_expenses, 'total_expense': total_expense, 'planned_budget': planned_budget})


def expense_summary_top(request, year, month):
    queryset = Expense.objects.filter(date__year=year, date__month=month, is_saving=False)
    serializer = ExpenseDisplaySerializer(queryset, many=True)
    categories = Category.objects.all()
    expenses = Expense.objects.filter(date__year=year, date__month=month, is_saving=False).values('category__name').annotate(total=Sum('amount'))
    total_expense = round(sum(float(expense['amount']) for expense in serializer.data), 2)

    category_expenses = []
    planned_budget = 0
    for category in categories:
        expense = next((x for x in expenses if x['category__name'] == category.name), None)
        if expense:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            total = float(expense['total'])
            planned_budget = planned_budget + round(budget.start_balance, 2)

            expenses_list = ExpenseSerializer(
                            Expense.objects.filter(date__year=year, date__month=month, category=category),
                            many=True,
                            context={'request': request}  # Pass the request context to the serializer
                        ).data

            for  expense_item in expenses_list:
                expense_item['tag'] = TagSerializer(
                    Tag.objects.get(id=expense_item['tag']),  # Fetch the Tag object by ID
                    context={'request': request}  # Pass the request context to the serializer
                ).data

            category_expenses.sort(key=lambda x: x['total'], reverse=True)

            category_expenses.append({
            'name': category.name,
            'total': round(total, 2),
            'planned_expense': planned_expense,
            'expenses': expenses_list

        })
        else:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({
                'name': category.name,
                'total': 0,
                'planned_expense': planned_expense,
                'expenses': list(Expense.objects.filter(date__year=year, date__month=month, category=category).values())
            })
        top_expenses = category_expenses[:5]
    return JsonResponse({'expenses': top_expenses, 'total_expense': total_expense, 'planned_budget': planned_budget})

@api_view(['GET'])
def expense_by_category(request, year, category_name):
    # Retrieve the category object based on the provided name
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

    # Filter expenses for the specified category and year
    queryset = Expense.objects.filter(
        category=category,
        date__year=year,
        is_saving=False
    )

    # Serialize the expenses
    serializer = ExpenseSerializer(queryset, many=True)

    # Group expenses by all months in the year
    all_months = range(1, 13)  # All months in a year
    monthly_expenses = (
        queryset.annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
    )

    monthly_expenses_data = [
        {
            'month': calendar.month_name[month],
            'total_expense': int(expense['total']) if 'total' in expense else 0,
        }
        for month in all_months
        for expense in monthly_expenses
        if expense.get('month') == month
    ]

    response_data = {
        'monthly_expenses': monthly_expenses_data,
        'category_name': category_name,
    }

    return JsonResponse(response_data)


@api_view(['GET'])
def expense_by_category_total(request, from_year, to_year, category_name):
    # Retrieve the category object based on the provided name
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

    # Filter expenses for the specified category and year
    queryset = Expense.objects.filter(
        category=category,
        date__year__range=(from_year, to_year),
        is_saving=False
    )

    # Group expenses by year
    yearly_expenses = (
        queryset.annotate(year=ExtractYear('date'))
        .values('year')
        .annotate(total=Sum('amount'))
        .order_by('year')
    )

    # Create a list of total expenses for each year
    all_years = range(from_year, to_year + 1)
    yearly_expenses_data = [
        {
            'year': year,
            'total_expense': int(round(next((expense['total'] for expense in yearly_expenses if expense['year'] == year), 0), 2))
        }
        for year in all_years
    ]

    response_data = {
        'yearly_expenses': yearly_expenses_data,
        'category_name': category_name,
    }

    return JsonResponse(response_data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def expense_yearly_totals(request, year):
    queryset = Expense.objects.filter(date__year=year, is_saving=False)
    serializer = ExpenseSerializer(queryset, many=True)
    categories = Category.objects.all()

    expenses = Expense.objects.filter(date__year=year).values('category__name').annotate(total=Sum('amount'))
    total_expense = round(sum(float(expense['amount']) for expense in serializer.data), 2)

    category_expenses = []
    planned_budget = 0
    for category in categories:
        expense = next((x for x in expenses if x['category__name'] == category.name), None)
        if expense:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            total = float(expense['total'])
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({'name': category.name, 'total': round(total, 2), 'planned_expense': planned_expense})
        else:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({'name': category.name, 'total': 0, 'planned_expense': planned_expense})

    return JsonResponse({'year': year, 'expenses': category_expenses, 'total_expense': total_expense, 'planned_budget': planned_budget})


@api_view(['GET'])
def expense_year_monthly(request, year):
    # Get all months within the specified year
    months = [str(month) for month in range(1, 13)]
    month_names = [calendar.month_name[int(month)] for month in months]

    # Initialize a list to store monthly totals as objects  
    yearly_expenses = []

    # Loop through each month and calculate expenses
    for month, month_name in zip(months, month_names):
        # Calculate the total expenses for each category in the specified month and year
        expenses = Expense.objects.filter(date__year=year, date__month=month, is_saving=False) \
            .values('category__name') \
            .annotate(total=Coalesce(Sum(F('amount')), 0.0, output_field=fields.FloatField()))

        # Calculate the total expenses for this month
        total_expense = round(sum(expense['total'] for expense in expenses), 2)

        # Append the monthly total as an object to the list
        yearly_expenses.append({'name': month_name, 'value': total_expense})

    # Calculate the total planned budget for the year
    categories = Category.objects.all()
    planned_budget = sum(budget.start_balance for budget in Budget.objects.filter(category__in=categories))

    # Calculate the total actual expenses for the year
    total_expense = sum(expense['value'] for expense in yearly_expenses)

    response_data = {
        'year': year,
        'monthly_totals': yearly_expenses,
        'total_expense': round(total_expense, 2),
        'planned_budget': round(planned_budget, 2)
    }

    return JsonResponse(response_data)


@api_view(['GET'])
def expense_year_monthly_totals(request, start_year):
    # Determine the latest year available in the data
    latest_year = Expense.objects.aggregate(Max('date__year'))['date__year__max']

    # Ensure start_year is within a valid range
    start_year = max(start_year, 2000)  # Adjust the minimum year as needed
    start_year = min(start_year, latest_year)

    # Initialize a list to store yearly data
    yearly_data = []

    # Loop through each year from start_year to the latest year
    for year in range(start_year, latest_year + 1):
        # Get all months within the specified year
        months = [str(month) for month in range(1, 13)]
        month_names = [calendar.month_name[int(month)] for month in months]

        # Initialize a list to store monthly totals as objects
        yearly_expenses = []

        # Loop through each month and calculate expenses
        for month, month_name in zip(months, month_names):
            # Calculate the total expenses for each category in the specified month and year
            expenses = Expense.objects.filter(date__year=year, date__month=month, is_saving=False) \
                .values('category__name') \
                .annotate(total=Coalesce(Sum(F('amount')), 0.0, output_field=FloatField()))

            # Calculate the total expenses for this month
            total_expense = round(sum(expense['total'] for expense in expenses), 2)

            # Append the monthly total as an object to the list
            yearly_expenses.append({'name': month_name, 'value': total_expense})

        # Calculate the total planned budget for the year
        categories = Category.objects.all()
        planned_budget = sum(budget.start_balance for budget in Budget.objects.filter(category__in=categories))

        # Calculate the total actual expenses for the year
        total_expense = sum(expense['value'] for expense in yearly_expenses)

        # Append yearly data to the list
        yearly_data.append({
            'year': year,
            'monthly_totals': yearly_expenses,
            'total_expense': round(total_expense, 2),
            'planned_budget': round(planned_budget, 2)
        })

    return JsonResponse({'data': yearly_data})


@api_view(['GET'])
def expense_all_year_monthly_total(request, start_year):
    # Determine the latest year available in the data
    latest_year = Expense.objects.aggregate(Max('date__year'))['date__year__max']

    # Ensure start_year is within a valid range
    start_year = max(start_year, 2000)  # Adjust the minimum year as needed
    start_year = min(start_year, latest_year)

    # Initialize a list to store yearly data
    yearly_data = []

    # Loop through each year from start_year to the latest year
    for year in range(start_year, latest_year + 1):
        # Get all months within the specified year
        months = [str(month) for month in range(1, 13)]
        month_names = [calendar.month_name[int(month)] for month in months]

        # Initialize a list to store monthly totals as objects
        yearly_expenses = []

        # Loop through each month and calculate expenses
        for month, month_name in zip(months, month_names):
            # Calculate the total expenses for each category in the specified month and year
            expenses = Expense.objects.filter(date__year=year, date__month=month, is_saving=False) \
                .values('category__name') \
                .annotate(total=Coalesce(Sum(F('amount')), 0.0, output_field=FloatField()))

            # Calculate the total expenses for this month
            total_expense = round(sum(expense['total'] for expense in expenses), 2)

            # Append the monthly total as an object to the list
            yearly_expenses.append({'name': month_name, 'value': total_expense})

        # Calculate the total planned budget for the year
        categories = Category.objects.all()
        planned_budget = sum(budget.start_balance for budget in Budget.objects.filter(category__in=categories))

        # Calculate the total actual expenses for the year
        total_expense = sum(expense['value'] for expense in yearly_expenses)

        # Append yearly data to the list
        yearly_data.append({
            'year': year,
            'monthly_totals': yearly_expenses,
            'total_expense': round(total_expense, 2),
            'planned_budget': round(planned_budget, 2)
        })

    # Transform the data into the desired structure
    transformed_data = []

    # Loop through each month
    for month in range(1, 13):
        month_name = calendar.month_name[month]

        # Create a dictionary for the current month
        monthly_data = {'month': month_name}

        # Loop through each year and add the corresponding value to the dictionary
        for year_data in yearly_data:
            year = year_data['year']
            monthly_total = next((item['value'] for item in year_data['monthly_totals'] if item['name'] == month_name), 0)
            monthly_data[year] = monthly_total

        # Append the dictionary to the transformed_data list
        transformed_data.append(monthly_data)

    return JsonResponse({'data': transformed_data})


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def expense_list(request):
    # Extract query parameters
    category = request.query_params.get('category', None)
    month = request.query_params.get('month', None)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    sort_field = request.query_params.get('sort_field', 'date')
    sort_order = request.query_params.get('sort_order', 'asc')

    # Start with all expenses that are not savings
    expenses = Expense.objects.filter(is_saving=False)

    # Filter by category if provided
    if category:
        expenses = expenses.filter(category__name=category)

    # Filter by month if provided
    if month:
        expenses = expenses.filter(date__month=month)

    # Sorting logic based on query params
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'
    expenses = expenses.order_by(sort_field)

    # Pagination setup
    paginator = Paginator(expenses, page_size)
    paginated_expenses = paginator.get_page(page)

    # Serialize expenses into a structured response
    expenses_data = [
        {
            'type': 'expenses',
            'id': str(expense.id),  # Primary key of the expense
            'date': expense.date.isoformat(),  # String representation of date
            'amount': str(expense.amount),  # Amount as a string
            'tag': {
                'id': str(expense.tag.id),  # Tag ID
                'name': expense.tag.name,  # Tag name
                # Add any other fields you want to return from the Tag model
            } if expense.tag else {},  # Include the tag object, or empty dict if no tag
            'category': {
                'id': str(expense.category.id),  # Category ID
                'name': expense.category.name,  # Category name
            } if expense.category else {},  # Include the category object, or empty dict if no category
            'payment_method': expense.payment_method,  # Payment method
            'account': {
                'id': str(expense.account.id),  # Account ID
                'name': expense.account.name,  # Account name
            } if expense.account else {},  # Include the account object, or empty dict if no account
            'description': expense.description,  # Description of the expense
        }
        for expense in paginated_expenses
    ]

    # Return paginated expenses in the response
    return JsonResponse({
        'data': expenses_data,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_items': paginator.count,
    })
    category = request.query_params.get('category', None)
    month = request.query_params.get('month', None)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    sort_field = request.query_params.get('sort_field', 'date')
    sort_order = request.query_params.get('sort_order', 'asc')

    expenses = Expense.objects.filter(is_saving=False)

    if category:
        expenses = expenses.filter(category__name=category)

    if month:
        expenses = expenses.filter(date__month=month)

    # Sorting logic
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'
    expenses = expenses.order_by(sort_field)

    # Pagination logic
    paginator = Paginator(expenses, page_size)
    paginated_expenses = paginator.get_page(page)

    expenses_data = [
        {
            'type': 'expenses',
            'id': str(expense.id),
            'date': expense.date.isoformat(),
            'amount': str(expense.amount),
            'tag_name': expense.tag.name,
            'category': expense.category.name,
            'payment_method': expense.payment_method,
            'account': expense.account.name,
            'description': expense.description,
        }
        for expense in paginated_expenses
    ]

    return JsonResponse({
        'data': expenses_data,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_items': paginator.count,
    })


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def expenses_by_tag(request):
    # Get parameters from the request
    tag_id = request.GET.get('tag_id')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Query expenses based on tag, year, and month
    expenses = Expense.objects.filter(
        tag_id=tag_id,
        date__year=year,
        date__month=month,
        is_saving=False
    )

    # Serialize the expenses
    serialized_expenses = ExpenseSerializer(expenses, many=True).data

    total_monthly_amount = round(sum(float(expense['amount']) for expense in serialized_expenses), 2)

    # Calculate the total tag data for the entire year
    expenses_yearly = Expense.objects.filter(
        tag_id=tag_id,
        date__year=year
    )
    total_yearly_amount = round(sum(float(expense.amount) for expense in expenses_yearly), 2)

    return JsonResponse({
        'expenses': serialized_expenses,
        'total_monthly_amount': total_monthly_amount,
        'total_yearly_amount': total_yearly_amount
    })


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

@api_view(['POST'])
def create_expense(request):
    serializer = ExpenseSerializer(data=request.data)
    print(serializer)
    
    if serializer.is_valid():
        # Get the category and tag objects from the foreign keys
        category = get_object_or_404(Category, pk=request.data['category'])
        tag = get_object_or_404(Tag, pk=request.data['tag'])
        account = get_object_or_404(Account, pk=request.data['account'])
        user = get_object_or_404(User, pk=request.data['user'])

        # # Create the expense object with the validated serializer data and related objects
        expense = serializer.save(category=category,account=account, tag=tag, user=user)

        # print(expense)

        # # # Set the payment method based on the foreign key
        # payment_method = request.data['payment_method']

        # # # Set the payment method based on the foreign key
        # account = request.data['account']
        # # expense.payment_method = payment_method
        # # expense.save()

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def get_monthly_expense_total(request):
    """
    Get total expense for the current month, considering date ranges.
    """
    today = datetime.today()

    # Filter expenses where date falls within the current month and year
    monthly_expense_total = Expense.objects.filter(
        date__month=today.month,
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({'monthly_expense_total': monthly_expense_total})
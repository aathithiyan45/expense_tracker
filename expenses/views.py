from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.utils.timezone import now
from .models import Expense, Category
from .forms import ExpenseForm

def login_or_signup(request):
    """View to handle login and provide an option to sign up."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            send_mail(
                'Login Notification',
                f'Hi {user.username},\n\nYou successfully logged in on {now().strftime("%Y-%m-%d %H:%M:%S")}.',
                'from-email@example.com',  # Replace with your sender email
                [user.email],
                fail_silently=False,
            )
            return redirect('index')  # Redirect to the homepage after login
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login_or_signup.html', {'form': form})
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def signup(request):
    """View to handle user signup."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_or_signup')  # Redirect to the login page after successful signup
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

from django.db.models import Sum

@login_required
def index(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_filter = request.GET.get('category_filter')

    expenses = Expense.objects.filter(user=request.user)

    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)

    # Calculate total expenses
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Get highest spending category
    highest_spending = expenses.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total').first()

    # Get total number of transactions
    total_transactions = expenses.count()

    # Get category-wise breakdown
    category_totals = expenses.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Get specific category totals
    food_expenses = expenses.filter(category__name='Food').aggregate(Sum('amount'))['amount__sum'] or 0
    travel_expenses = expenses.filter(category__name='Travel').aggregate(Sum('amount'))['amount__sum'] or 0
    housing_expenses = expenses.filter(category__name='Housing').aggregate(Sum('amount'))['amount__sum'] or 0
    healthcare_expenses = expenses.filter(category__name='Healthcare').aggregate(Sum('amount'))['amount__sum'] or 0
    shopping_expenses = expenses.filter(category__name='Shopping').aggregate(Sum('amount'))['amount__sum'] or 0
    other_expenses = expenses.exclude(
        category__name__in=['Food', 'Travel', 'Housing', 'Healthcare', 'Shopping']
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate percentages for category cards
    if total_expense > 0:
        food_expenses_percent = (food_expenses / total_expense) * 100
        travel_expenses_percent = (travel_expenses / total_expense) * 100
        shopping_expenses_percent = (shopping_expenses / total_expense) * 100
        other_expenses_percent = (other_expenses / total_expense) * 100
    else:
        food_expenses_percent = travel_expenses_percent = shopping_expenses_percent = other_expenses_percent = 0

    # Get expense trend data (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    
    last_week = timezone.now().date() - timedelta(days=7)
    expense_trend = expenses.filter(
        date__gte=last_week
    ).values('date').annotate(
        total=Sum('amount')
    ).order_by('date')

    # Prepare category distribution data
    category_distribution = list(category_totals.values('category__name', 'total'))

    # Get recent transactions for dashboard
    recent_transactions = expenses.order_by('-date')[:5]

    # Calculate month-to-date and year-to-date expenses
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(month=1, day=1)
    
    mtd_expenses = expenses.filter(date__gte=first_day_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
    ytd_expenses = expenses.filter(date__gte=first_day_of_year).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_expense': total_expense,
        'highest_spending': highest_spending['category__name'] if highest_spending else None,
        'highest_spending_amount': highest_spending['total'] if highest_spending else 0,
        'total_transactions': total_transactions,
        'food_expenses': food_expenses,
        'travel_expenses': travel_expenses,  # Fixed: using travel_expenses instead of transport_expenses
        'shopping_expenses': shopping_expenses,
        'other_expenses': other_expenses,
        
        # Percentages for category cards
        'food_expenses_percent': food_expenses_percent,
        'travel_expenses_percent': travel_expenses_percent,
        'shopping_expenses_percent': shopping_expenses_percent,
        'other_expenses_percent': other_expenses_percent,
        
        'expense_trend': list(expense_trend),
        'category_distribution': category_distribution,
        'categories': Category.objects.all(),
        'recent_transactions': recent_transactions,
        'mtd_expenses': mtd_expenses,
        'ytd_expenses': ytd_expenses,
    }

    return render(request, 'expenses/index.html', context)


@login_required
def add_expense(request):
    categories = Category.objects.all()
    today_date = now().date()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        custom_category = request.POST.get('custom_category')  # Get the custom category if provided

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Attach the logged-in user

            # Handle custom category
            if custom_category:
                # Check if custom category already exists, if not, create it
                category, created = Category.objects.get_or_create(name=custom_category)
                expense.category = category
            else:
                # If no custom category, use the selected category
                expense.category = form.cleaned_data['category']

            expense.save()
            print(expense.__dict__)  # Debugging: Prints all fields and values of the Expense object
            send_mail(
                'New Expense Added',
                f'Expense added successfully.',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
            # Corrected email notification
            send_mail(
                'New Expense Added',
                f'You have added a new expense in category ID: {expense.category_id} for ${expense.amount}. '
                f'Description: {expense.description if expense.description else "No description provided"}.',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
            return redirect('index')
    else:
        form = ExpenseForm()

    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'categories': categories,
        'today_date': today_date,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)  # Ensure the expense belongs to the user
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            # Send email after editing
            send_mail(
                'Expense Updated',
                f'Your expense "{expense.category}" has been updated successfully.',
                'from-email@example.com',  # Sender's email
                [request.user.email],  # Recipient's email (assuming user is logged in)
                fail_silently=False,
            )
            return redirect('index')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)  # Ensure the expense belongs to the user
    if request.method == 'POST':
        expense.delete()
        # Send email after deletion
        send_mail(
            'Expense Deleted',
            f'Your expense "{expense.category}" has been deleted successfully.',
            'from-email@example.com',  # Sender's email
            [request.user.email],  # Recipient's email (assuming user is logged in)
            fail_silently=False,
        )
        return redirect('index')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

from django.shortcuts import redirect
from django.contrib.auth import logout

def custom_logout(request):
    """Logs out the user and redirects to homepage."""
    logout(request)
    return redirect('index')  # Redirect to homepage or any other page after logout
from django.db.models import Sum
from django.db.models.functions import TruncWeek
from django.shortcuts import render
from .models import Expense

def weekly_summary(request):
    # Group by week and category, then calculate the total amount for each group
    expenses = (
        Expense.objects.filter(user=request.user)
        .annotate(week=TruncWeek('date'))  # Group by week
        .values('week', 'category')  # Group by both week and category
        .annotate(total_amount=Sum('amount'))  # Calculate the total amount per category per week
        .order_by('week', 'category')  # Sort by week and category
    )

    # Render the expenses to the template
    return render(request, 'expenses/weekly_summary.html', {'expenses': expenses})
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg for non-GUI environments
import io
import base64
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from .models import Expense, Category
from django.contrib.auth.decorators import login_required

@login_required
def monthly_summary(request):
    # Step 1: Get the total expense per month for the user
    monthly_totals_raw = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))  # Group by month
        .values('month')  # Only need the month
        .annotate(total_amount=Sum('amount'))  # Calculate the total amount per month
        .order_by('month')  # Sort by month
    )

    # Format data for table rendering
    monthly_totals = [
        {
            'month': entry['month'].strftime("%B %Y"),  # Format the month as "Month Year"
            'total_amount': entry['total_amount'],  # Total expense for the month
        }
        for entry in monthly_totals_raw
    ]

    # Step 2: Prepare data for the graph
    month_labels = [entry['month'].strftime("%B %Y") for entry in monthly_totals_raw]  # Month labels
    total_expenses_values = [entry['total_amount'] for entry in monthly_totals_raw]  # Total expenses

    if not month_labels:  # Handle case where there is no data
        month_labels = ["No Data"]
        total_expenses_values = [0]

    # Step 3: Generate the graph
    plt.figure(figsize=(10, 6))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']  # Pre-defined colors

    # Plot horizontal bar chart
    plt.barh(month_labels, total_expenses_values, color=colors[:len(month_labels)], edgecolor='black', height=0.5)
    plt.ylabel('Month', fontsize=14, fontweight='bold')
    plt.xlabel('Total Expense', fontsize=14, fontweight='bold')
    plt.title('Monthly Expense Summary', fontsize=16, fontweight='bold')
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Add annotations for expense values
    for i, value in enumerate(total_expenses_values):
        plt.text(value + 5, i, f"${value:.2f}", va='center', fontsize=10, color='black')

    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    # Pass data to the template
    return render(request, 'expenses/monthly_summary.html', {
        'chart_image': image_base64,
        'monthly_totals': monthly_totals,
    })
from django.db.models.functions import TruncWeek

@login_required
def weekly_summary(request):
    # Step 1: Get total expenses grouped by week
    weekly_totals_raw = (
        Expense.objects.filter(user=request.user)
        .annotate(week=TruncWeek('date'))  # Group by week
        .values('week')  # Only need the week
        .annotate(total_amount=Sum('amount'))  # Calculate total expense per week
        .order_by('week')  # Sort by week
    )

    # Format data for table rendering
    weekly_totals = [
        {
            'week': entry['week'].strftime("Week of %d %B %Y"),  # Format as "Week of DD Month YYYY"
            'total_amount': entry['total_amount'],
        }
        for entry in weekly_totals_raw
    ]

    # Step 2: Prepare data for the graph
    week_labels = [entry['week'].strftime("Week of %d %B") for entry in weekly_totals_raw]
    total_expenses_values = [entry['total_amount'] for entry in weekly_totals_raw]

    if not week_labels:  # Handle no data case
        week_labels = ["No Data"]
        total_expenses_values = [0]

    # Generate the horizontal bar chart
    plt.figure(figsize=(10, 6))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    plt.barh(week_labels, total_expenses_values, color=colors[:len(week_labels)], edgecolor='black', height=0.5)
    plt.ylabel('Week', fontsize=14, fontweight='bold')
    plt.xlabel('Total Expense', fontsize=14, fontweight='bold')
    plt.title('Weekly Expense Summary', fontsize=16, fontweight='bold')
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Add annotations
    for i, value in enumerate(total_expenses_values):
        plt.text(value + 5, i, f"${value:.2f}", va='center', fontsize=10, color='black')

    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    # Pass data to the template
    return render(request, 'expenses/weekly_summary.html', {
        'chart_image': image_base64,
        'weekly_totals': weekly_totals,
    })
from django.db.models.functions import ExtractYear

@login_required
def yearly_summary(request):
    # Step 1: Get total expenses grouped by year
    yearly_totals_raw = (
        Expense.objects.filter(user=request.user)
        .annotate(year=ExtractYear('date'))  # Extract year
        .values('year')  # Only need the year
        .annotate(total_amount=Sum('amount'))  # Calculate total expense per year
        .order_by('year')  # Sort by year
    )

    # Format data for table rendering
    yearly_totals = [
        {
            'year': entry['year'],  # The year
            'total_amount': entry['total_amount'],
        }
        for entry in yearly_totals_raw
    ]

    # Step 2: Prepare data for the graph
    year_labels = [entry['year'] for entry in yearly_totals_raw]
    total_expenses_values = [entry['total_amount'] for entry in yearly_totals_raw]

    if not year_labels:  # Handle no data case
        year_labels = ["No Data"]
        total_expenses_values = [0]

    # Generate the horizontal bar chart
    plt.figure(figsize=(10, 6))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    plt.barh(year_labels, total_expenses_values, color=colors[:len(year_labels)], edgecolor='black', height=0.5)
    plt.ylabel('Year', fontsize=14, fontweight='bold')
    plt.xlabel('Total Expense', fontsize=14, fontweight='bold')
    plt.title('Yearly Expense Summary', fontsize=16, fontweight='bold')
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Add annotations
    for i, value in enumerate(total_expenses_values):
        plt.text(value + 5, i, f"${value:.2f}", va='center', fontsize=10, color='black')

    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    # Pass data to the template
    return render(request, 'expenses/yearly_summary.html', {
        'chart_image': image_base64,
        'yearly_totals': yearly_totals,
    })
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm  # Assuming you have a form for Profile

@login_required
def profile_view(request):
    # Ensure the profile exists or create one
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'expenses/profile.html', {'profile': profile})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone  # Import timezone
from .forms import ProfileForm

@login_required
def update_profile(request):
    profile = request.user.profile  # Assuming a one-to-one relation
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile
            # Send email notification
            send_mail(
                'Profile Updated Successfully',
                f'Hi {request.user.username},\n\nYour profile was updated on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}.',
                'from-email@example.com',  # Sender's email
                [request.user.email],  # Recipient's email
                fail_silently=False,
            )
            return redirect('profile')  # Redirect to the profile view page
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'expenses/profile_update.html', {'form': form})


@login_required
def expenses_list(request):
    """View to display all expenses."""
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_filter = request.GET.get('category_filter')
    
    # Apply filters if provided
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)
    
    # Calculate total filtered expenses
    total_filtered = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'expenses': expenses,
        'total_filtered': total_filtered,
        'categories': Category.objects.all(),
    }
    
    return render(request, 'expenses/expenses_list.html', context)

@login_required
def categories(request):
    """
    View to display all expense categories and allow adding new ones.
    """
    # Get all categories for the current user
    categories = Category.objects.filter(user=request.user)
    
    # Handle form submission for adding a new category
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        color = request.POST.get('color', '#4A90E2')
        
        if name:
            # Create new category
            Category.objects.create(
                user=request.user,
                name=name,
                description=description,
                color=color
            )
            return redirect('categories')
    
    # Render the categories template with the list of categories
    return render(request, 'expenses/categories.html', {
        'categories': categories
    })

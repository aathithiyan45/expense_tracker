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
            return redirect('index')  # Redirect to the homepage after login
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login_or_signup.html', {'form': form})

def signup(request):
    """View to handle user signup."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_or_signup')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()

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

    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    category_breakdown = expenses.values('category__name').annotate(total=Sum('amount')).order_by('category__name')
    category_breakdown = {item['category__name']: item['total'] for item in category_breakdown}

    categories = Category.objects.all()  # For filter dropdown

    return render(request, 'expenses/index.html', {
        'expenses': expenses,
        'total_expense': total_expense,
        'category_breakdown': category_breakdown,
        'categories': categories,

    })


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
            return redirect('index')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)  # Ensure the expense belongs to the user
    if request.method == 'POST':
        expense.delete()
        return redirect('index')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.utils.timezone import now

@login_required
def dashboard(request):
    # Example data for the dashboard
    expenses = Expense.objects.filter(user=request.user)
    total_monthly_expense = expenses.filter(date__month=now().month).aggregate(Sum('amount'))['amount__sum'] or 0

    # Category-wise breakdown
    category_breakdown = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    top_category = category_breakdown.first() if category_breakdown else None

    recent_expenses = expenses.order_by('-date')[:5]

    return render(request, 'dashboard.html', {
        'total_monthly_expense': total_monthly_expense,
        'top_category': top_category,
        'recent_expenses': recent_expenses,
    })
from django.shortcuts import redirect
from django.contrib.auth import logout

def custom_logout(request):
    """Logs out the user and redirects to homepage."""
    logout(request)
    return redirect('index')  # Redirect to homepage or any other page after logout

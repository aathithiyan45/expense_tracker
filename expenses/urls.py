from django.urls import path
from django.contrib.auth.views import LogoutView  # Import Django's built-in LogoutView
from . import views

urlpatterns = [
    path('', views.login_or_signup, name='login_or_signup'),  # Default login or signup page
    path('signup/', views.signup, name='signup'),  # Signup page
    path('logout/', LogoutView.as_view(next_page='login_or_signup'), name='logout'),  # Logout page
    path('index/', views.index, name='index'),  # Expense listing page
    path('add/', views.add_expense, name='add_expense'),  # Add expense page
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),  # Edit expense page
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),  # Delete expense page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
]

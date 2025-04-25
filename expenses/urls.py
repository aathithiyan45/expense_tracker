from django.urls import path
from django.contrib.auth.views import LogoutView  # Import Django's built-in LogoutView
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import profile_view

urlpatterns = [
    path('', views.login_or_signup, name='login_or_signup'),  # Default login or signup page
    path('signup/', views.signup, name='signup'),  # Signup page
    path('logout/', LogoutView.as_view(next_page='login_or_signup'), name='logout'),  # Logout page
    path('index/', views.index, name='index'),  # Expense listing page
    path('add/', views.add_expense, name='add_expense'),  # Add expense page
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),  # Edit expense page
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),  # Delete expense page
    path('summary/weekly/', views.weekly_summary, name='weekly_summary'),
    path('summary/monthly/', views.monthly_summary, name='monthly_summary'),
    path('summary/yearly/', views.yearly_summary, name='yearly_summary'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='profile_update'),  # Update profile
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import profile_view

urlpatterns = [
    # Authentication URLs
    path('', views.login_or_signup, name='login_or_signup'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login_or_signup'), name='logout'),
    
    # Main Expense URLs
    path('index/', views.index, name='index'),
    path('add/', views.add_expense, name='add_expense'),
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    
    # Summary URLs
    path('categories/', views.categories, name='categories'),
    path('summary/weekly/', views.weekly_summary, name='weekly_summary'),
    path('summary/monthly/', views.monthly_summary, name='monthly_summary'),
    path('summary/yearly/', views.yearly_summary, name='yearly_summary'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='profile_update'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




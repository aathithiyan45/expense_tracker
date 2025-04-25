from django.contrib import admin
from .models import Category, Expense

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the category name in the list
    search_fields = ('name',)  # Allow searching by category name
    ordering = ('name',)  # Ordering by category name

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'description', 'date')  # Columns to display in the list
    list_filter = ('category', 'date')  # Filters to allow filtering by category and date
    search_fields = ('description', 'category__name')  # Allow searching by description and category name
    list_per_page = 20  # Show 20 entries per page
    ordering = ('-date',)  # Default ordering by date, descending

# Register the models with the admin interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Expense, ExpenseAdmin)

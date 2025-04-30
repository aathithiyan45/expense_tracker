from django import forms
from django.contrib.auth.forms import UserCreationForm  # Add this import
from django.contrib.auth.models import User
from .models import Expense, Category, Profile

class ExpenseForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add a new category if not listed',
            'class': 'form-control'
        }),
        label="Other Category (Optional)"
    )

    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select category'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description',
                'rows': 3
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }
        labels = {
            'category': 'Expense Category',
            'amount': 'Amount ($)',
            'description': 'Description',
            'date': 'Date of Expense'
        }
        help_texts = {
            'category': 'Select an existing category or create a new one below',
            'amount': 'Enter the expense amount in dollars',
            'description': 'Provide details about the expense',
            'date': 'Select the date when the expense occurred'
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("The amount must be a positive number.")
        if amount > 1000000:
            raise forms.ValidationError("Amount cannot exceed $1,000,000.")
        return amount

    def clean_new_category(self):
        new_category = self.cleaned_data.get('new_category')
        if new_category and Category.objects.filter(name=new_category).exists():
            raise forms.ValidationError(
                f"The category '{new_category}' already exists. Please select it from the list.")
        return new_category

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

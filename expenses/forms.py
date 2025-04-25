from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Add a new category if not listed'}),
        label="Other Category (Optional)"
    )

    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Custom validation for the 'amount' field
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError("The amount must be a positive number.")

        return amount

    # Optionally, you can also add validation for the custom category (as shown in previous examples)
    def clean_new_category(self):
        new_category = self.cleaned_data.get('new_category')

        # Check if new category is not empty and only allow valid category names
        if new_category and Category.objects.filter(name=new_category).exists():
            raise forms.ValidationError(
                f"The category '{new_category}' already exists. Please select it from the list.")

        return new_category
from django import forms
from .models import Profile  # Make sure this line is present

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

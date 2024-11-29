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

from django import forms 
from .models import Account

class NewAccountsCSVForm(forms.Form):
    file = forms.FileField()


class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=Account.objects.all().order_by("name"))
    to_account = forms.ModelChoiceField(queryset=Account.objects.all().order_by("name"))
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

 
class NewAccountForm(forms.Form):
    id = forms.UUIDField()
    name = forms.CharField(max_length=40)
    balance = forms.FloatField(min_value=0)
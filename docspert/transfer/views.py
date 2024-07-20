from django.views.generic import TemplateView, ListView, FormView, DetailView, CreateView
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Account
from .forms import NewAccountsCSVForm, TransferForm, NewAccountForm



class HomeView(TemplateView):
    template_name = 'transfer/home.html'


class AccountListView(ListView):
    model = Account
    template_name = 'account_list.html'
    context_object_name = 'accounts'
    ordering = "name"

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        min_balance = self.request.GET.get('min_balance')
        max_balance = self.request.GET.get('max_balance')
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if min_balance:
            queryset = queryset.filter(balance__gte=min_balance)
        if max_balance:
            queryset = queryset.filter(balance__lte=max_balance)
            
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = NewAccountForm()
        return context
    

class AccountDetailView(DetailView):
    model = Account
    template_name = 'transfer/account_detail.html'
    context_object_name = 'account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sent_transactions'] = self.object.sent_transactions.all()
        context['received_transactions'] = self.object.received_transactions.all()
        return context


class UploadFileView(FormView):
    template_name = 'transfer/upload.html'
    form_class = NewAccountsCSVForm
    success_url = reverse_lazy('transfer:account-list')

    def form_valid(self, form):
        file = form.cleaned_data['file']
        try:
            Account.import_data(file)
            return super().form_valid(form)
        except ValueError as e:
            return render(self.request, 'transfer/import_failed.html', {'error': str(e)})

class AddAccountView(CreateView):
    template_name = 'transfer/add_account.html'
    # form_class = NewAccountForm
    fields = ["name", "balance"]
    model = Account
    success_url = reverse_lazy('transfer:account-list')


class TransferView(FormView):
    template_name = 'transfer/transfer.html'
    form_class = TransferForm
    success_url = reverse_lazy('transfer:account-list')

    def form_valid(self, form):
        from_account = form.cleaned_data['from_account']
        to_account = form.cleaned_data['to_account']
        amount = float(form.cleaned_data['amount']) 
        if from_account.fund_transfer(to_account, amount):
            return super().form_valid(form)
        elif amount < 0:
            form.add_error(None, 'Invalid transfer amount.')
            return self.form_invalid(form)    
        else:
            form.add_error(None, 'Insufficient balance in the source account.')
            return self.form_invalid(form)
from django.test import TestCase
from ..forms import NewAccountsCSVForm, TransferForm, NewAccountForm
from ..models import Account
from django.core.files.uploadedfile import SimpleUploadedFile
from uuid import uuid4

class FormTests(TestCase):

    def test_new_accounts_csv_form_valid(self):
        file = SimpleUploadedFile("file.csv", b"file_content", content_type="text/csv")
        form = NewAccountsCSVForm(data={}, files={'file': file})
        self.assertTrue(form.is_valid())

    def test_new_accounts_csv_form_invalid(self):
        form = NewAccountsCSVForm(data={}, files={})
        self.assertFalse(form.is_valid())

    def test_transfer_form_valid(self):
        account1 = Account.objects.create(name="Account 1", balance=1000)
        account2 = Account.objects.create(name="Account 2", balance=1000)
        form_data = {
            'from_account': account1.uuid,
            'to_account': account2.uuid,
            'amount': 100.00
        }
        form = TransferForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_transfer_form_invalid_missing_fields(self):
        form_data = {
            'from_account': '',
            'to_account': '',
            'amount': ''
        }
        form = TransferForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_new_account_form_valid(self):
        form_data = {
            'id': uuid4(),
            'name': 'New Account',
            'balance': 1000.00
        }
        form = NewAccountForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_new_account_form_invalid_missing_fields(self):
        form_data = {
            'id': '',
            'name': '',
            'balance': ''
        }
        form = NewAccountForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_new_account_form_invalid_negative_balance(self):
        form_data = {
            'id': uuid4(),
            'name': 'New Account',
            'balance': -1000.00
        }
        form = NewAccountForm(data=form_data)
        self.assertFalse(form.is_valid())

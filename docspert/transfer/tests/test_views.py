# transfer_app/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Account, Transaction
from decimal import Decimal

class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('transfer:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/home.html')


class AccountListViewTest(TestCase):
    def setUp(self):
        self.account1 = Account.objects.create(name="Alice", balance=Decimal('1000.00'))
        self.account2 = Account.objects.create(name="Bob", balance=Decimal('500.00'))

    def test_account_list_view(self):
        response = self.client.get(reverse('transfer:account-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/account_list.html')
        self.assertContains(response, self.account1.name)
        self.assertContains(response, self.account2.name)

    def test_account_list_view_filtering_by_name(self):
        response = self.client.get(reverse('transfer:account-list'), {'name': 'Alice'})
        self.assertContains(response, self.account1.name)
        self.assertNotContains(response, self.account2.name)

    def test_account_list_view_filtering_by_max_balance(self):
        response = self.client.get(reverse('transfer:account-list'), {'min_balance': '700'})
        self.assertContains(response, self.account1.name)
        self.assertNotContains(response, self.account2.name)

    def test_account_list_view_filtering_by_min_balance(self):
        response = self.client.get(reverse('transfer:account-list'), {'max_balance': '700'})
        self.assertContains(response, self.account2.name)
        self.assertNotContains(response, self.account1.name)


class AccountDetailViewTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(name="Alice", balance=Decimal('1000.00'))

    def test_account_detail_view(self):
        response = self.client.get(reverse('transfer:account-detail', args=[self.account.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/account_detail.html')
        self.assertContains(response, self.account.name)


class UploadFileViewTest(TestCase):
    def test_upload_file_view_get(self):
        response = self.client.get(reverse('transfer:file-upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/upload.html')

    def test_upload_file_view_post_valid_csv(self):
        test_file = SimpleUploadedFile(
            "test.csv",
            b"ID,Name,Balance\n33333333-3333-3333-3333-333333333333,Account 3,1000.00",
            content_type="text/csv"
        )
        response = self.client.post(reverse('transfer:file-upload'), {'file': test_file})
        self.assertRedirects(response, reverse('transfer:account-list'))
        self.assertEqual(Account.objects.count(), 1)
        account = Account.objects.get(uuid="33333333-3333-3333-3333-333333333333")
        self.assertEqual(account.name, "Account 3")
        self.assertEqual(account.balance, Decimal('1000.00'))

    def test_upload_file_view_post_invalid_file(self):
        test_file = SimpleUploadedFile(
            "test.txt",
            b"ID,Name,Balance\n33333333-3333-3333-3333-333333333333,Account 3,1000.00",
            content_type="text/plain"
        )
        response = self.client.post(reverse('transfer:file-upload'), {'file': test_file})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/import_failed.html')
        self.assertContains(response, 'Unsupported file type')
        self.assertEqual(Account.objects.count(), 0)


class AddAccountViewTest(TestCase):
    def test_add_account_view_get(self):
        response = self.client.get(reverse('transfer:add-account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/add_account.html')

    def test_add_account_view_post(self):
        response = self.client.post(reverse('transfer:add-account'), {'name': 'New Account', 'balance': '1000.00'})
        self.assertRedirects(response, reverse('transfer:account-list'))
        self.assertEqual(Account.objects.count(), 1)
        account = Account.objects.first()
        self.assertEqual(account.name, 'New Account')
        self.assertEqual(account.balance, Decimal('1000.00'))


class TransferViewTest(TestCase):
    def setUp(self):
        self.account1 = Account.objects.create(name="Alice", balance=Decimal('1000.00'))
        self.account2 = Account.objects.create(name="Bob", balance=Decimal('500.00'))

    def test_transfer_view_get(self):
        response = self.client.get(reverse('transfer:fund-transfer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/transfer.html')

    def test_transfer_view_post_valid(self):
        response = self.client.post(reverse('transfer:fund-transfer'), {
            'from_account': self.account1.uuid,
            'to_account': self.account2.uuid,
            'amount': '200.00'
        })
        self.assertRedirects(response, reverse('transfer:account-list'))
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('800.00'))
        self.assertEqual(self.account2.balance, Decimal('700.00'))

    def test_transfer_view_post_insufficient_funds(self):
        response = self.client.post(reverse('transfer:fund-transfer'), {
            'from_account': self.account1.uuid,
            'to_account': self.account2.uuid,
            'amount': '2000.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/transfer.html')
        self.assertContains(response, 'Insufficient balance in the source account.')
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('1000.00'))
        self.assertEqual(self.account2.balance, Decimal('500.00'))

    def test_transfer_view_post_invalid_value(self):
        response = self.client.post(reverse('transfer:fund-transfer'), {
            'from_account': self.account1.uuid,
            'to_account': self.account2.uuid,
            'amount': '-200.0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer/transfer.html')
        self.assertContains(response, 'Invalid transfer amount.')
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('1000.00'))
        self.assertEqual(self.account2.balance, Decimal('500.00'))
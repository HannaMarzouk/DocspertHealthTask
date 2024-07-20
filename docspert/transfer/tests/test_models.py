from django.test import TestCase
from ..models import Account, Transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from uuid import uuid4
from decimal import Decimal
import json
class AccountModelTest(TestCase):

    def setUp(self):
        Account.objects.create(uuid='12345678-1234-1234-1234-123456789012', name='Test Account 1', balance=100)
        Account.objects.create(uuid='12345678-1234-1234-1234-123456789013', name='Test Account 2', balance=200)

    def test_account_balance_transfer(self):
        account1 = Account.objects.get(name='Test Account 1')
        account2 = Account.objects.get(name='Test Account 2')
        amount = 50

        account1.balance -= amount
        account2.balance += amount

        account1.save()
        account2.save()

        self.assertEqual(account1.balance, 50)
        self.assertEqual(account2.balance, 250)

    def test_account_balance_transfer(self):
        account1 = Account.objects.get(name='Test Account 1')
        self.assertEqual(account1.__str__(), "Test Account 1")

class AccountModelTransferTest(TestCase):
    def setUp(self):
        self.account1 = Account.objects.create(uuid=uuid4(), name="Account 1", balance=100.00)
        self.account2 = Account.objects.create(uuid=uuid4(), name="Account 2", balance=50.00)

    def test_transfer_success(self):
        self.assertTrue(self.account1.fund_transfer(self.account2, 50.00))
        self.assertEqual(self.account1.balance, 50.00)
        self.assertEqual(self.account2.balance, 100.00)

    def test_transfer_insufficient_funds(self):
        self.assertFalse(self.account1.fund_transfer(self.account2, 150.00))
        self.assertEqual(self.account1.balance, 100.00)
        self.assertEqual(self.account2.balance, 50.00)

    def test_transfer_invalid_funds(self):
        self.assertFalse(self.account1.fund_transfer(self.account2, -150.00))
        self.assertEqual(self.account1.balance, 100.00)
        self.assertEqual(self.account2.balance, 50.00)



class AccountModelImportTest(TestCase):
    def setUp(self):
        self.account1 = Account.objects.create(uuid=uuid4(), name="Account 1", balance=100.00)
        self.account2 = Account.objects.create(uuid=uuid4(), name="Account 2", balance=50.00)

    def test_import_accounts_csv(self):
        test_file = SimpleUploadedFile(
            "test.csv",
            b"ID,Name,Balance\n33333333-3333-3333-3333-333333333333,Account 3,1000.00",
            content_type="text/csv"
        )
        
        Account.import_data(test_file)
        
        self.assertEqual(Account.objects.count(), 3)
        account = Account.objects.get(uuid="33333333-3333-3333-3333-333333333333")
        self.assertEqual(account.name, "Account 3")
        self.assertEqual(account.balance, Decimal('1000.00'))

    def test_import_accounts_json(self):
        test_data = json.dumps([
            {"ID": "44444444-4444-4444-4444-444444444444", "Name": "Account 4", "Balance": "1500.00"}
        ])
        test_file = SimpleUploadedFile("test.json", test_data.encode('utf-8'), content_type="application/json")
        
        Account.import_data(test_file)
        
        self.assertEqual(Account.objects.count(), 3)
        account = Account.objects.get(uuid="44444444-4444-4444-4444-444444444444")
        self.assertEqual(account.name, "Account 4")
        self.assertEqual(account.balance, Decimal('1500.00'))

    def test_import_accounts_xml(self):
        test_data = """<?xml version="1.0"?>
        <Accounts>
            <Account>
                <ID>55555555-5555-5555-5555-555555555555</ID>
                <Name>Account 5</Name>
                <Balance>2000.00</Balance>
            </Account>
        </Accounts>"""
        test_file = SimpleUploadedFile("test.xml", test_data.encode('utf-8'), content_type="application/xml")
        
        Account.import_data(test_file)
        
        self.assertEqual(Account.objects.count(), 3)
        account = Account.objects.get(uuid="55555555-5555-5555-5555-555555555555")
        self.assertEqual(account.name, "Account 5")
        self.assertEqual(account.balance, Decimal('2000.00'))



class TransactionModelTest(TestCase):
    def setUp(self):
        self.account1 = Account.objects.create(
            uuid="11111111-1111-1111-1111-111111111111", 
            name="Account 1", 
            balance=float('1000.00')
        )
        self.account2 = Account.objects.create(
            uuid="22222222-2222-2222-2222-222222222222", 
            name="Account 2", 
            balance=float('500.00')
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            sender=self.account1,
            receive=self.account2,
            amount=float('100.00')
        )
        
        self.assertEqual(transaction.sender, self.account1)
        self.assertEqual(transaction.receive, self.account2)
        self.assertEqual(transaction.amount, float('100.00'))
        self.assertIsNotNone(transaction.timestamp)

    def test_related_name_outgoing_transactions(self):
        transaction = Transaction.objects.create(
            sender=self.account1,
            receive=self.account2,
            amount=float('100.00')
        )
        self.assertIn(transaction, self.account1.sent_transactions.all())

    def test_related_name_incoming_transactions(self):
        transaction = Transaction.objects.create(
            sender=self.account1,
            receive=self.account2,
            amount=float('100.00')
        )
        self.assertIn(transaction, self.account2.received_transactions.all())



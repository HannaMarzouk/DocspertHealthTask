from django.db import models
import uuid
from .importer import ImporterSelector


# Create your models here.
class Account(models.Model):
    uuid = models.UUIDField(verbose_name="ID", unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=40, help_text="Max 40 Characters")
    balance = models.FloatField(verbose_name="Balance", default=0.0)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def import_data(file):        
        file_type = file.name.split('.')[-1].lower()
        importer = ImporterSelector.get_importer(file_type)
        accounts_data = importer.import_accounts(file)
        for account_data in accounts_data:
            Account.objects.update_or_create(
                uuid=account_data['uuid'], 
                defaults={
                    'name': account_data['name'], 
                    'balance': account_data['balance']
                }
            )
        
    def fund_transfer(self, to_account, amount):
        if amount > 0 and amount < self.balance:
            self.balance -= amount
            to_account.balance += amount
            create_transaction = Transaction.objects.create(
                sender = self,
                receive = to_account,
                amount = amount
            )
            create_transaction.save()
            self.save() 
            to_account.save()
            return True
        else:
            return False
        

class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name= "sent_transactions")
    receive = models.ForeignKey(Account, on_delete=models.CASCADE, related_name= "received_transactions")
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
from abc import ABC, abstractmethod
import csv, json
import xml.etree.ElementTree as ET


class BaseImporter(ABC):
    @abstractmethod
    def import_accounts(self, file):
        pass

class CSVImporter(BaseImporter):
    def import_accounts(self, file):
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        accounts = []
        for row in reader:
            accounts.append({
                'uuid': row['ID'],
                'name': row['Name'],
                'balance': row['Balance']
            })
        return accounts

class JSONImporter(BaseImporter):
    def import_accounts(self, file):
        data = json.load(file)
        accounts = []
        for row in data:
            accounts.append({
                'uuid': row['ID'],
                'name': row['Name'],
                'balance': row['Balance']
            })
        return accounts


class XMLImporter(BaseImporter):
    def import_accounts(self, file):
        tree = ET.parse(file)
        root = tree.getroot()
        accounts = []
        for child in root:
            accounts.append({
                'uuid': child.find('ID').text,
                'name': child.find('Name').text,
                'balance': child.find('Balance').text
            })
        return accounts


class ImporterSelector:
    @staticmethod
    def get_importer(file_type):
        if file_type == 'csv':
            return CSVImporter()
        elif file_type == 'json':
            return JSONImporter()
        elif file_type == 'xml':
            return XMLImporter()
        else:
            raise ValueError("Unsupported file type please use: Csv/Json/XML")
        
        
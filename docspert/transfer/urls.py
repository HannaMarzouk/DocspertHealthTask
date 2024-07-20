from django.contrib import admin
from django.urls import path
from .views import HomeView, AccountListView, AccountDetailView, UploadFileView, TransferView, AddAccountView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('accounts/', AccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', AccountDetailView.as_view(), name='account-detail'),
    path('upload/', UploadFileView.as_view(), name='file-upload'),
    path('add/account/', AddAccountView.as_view(), name='add-account'),
    path('transfer/', TransferView.as_view(), name='fund-transfer'),
]
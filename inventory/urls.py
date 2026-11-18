
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('barang/tambah/', views.tambah_barang, name='tambah_barang'),
    path('barang/edit/<int:id>/', views.edit_barang, name='edit_barang'),
    path('barang/hapus/<int:id>/', views.hapus_barang, name='hapus_barang'),
]

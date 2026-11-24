from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Data Barang
    path('data-barang/', views.data_barang, name='data_barang'),

    # Tambah Barang
    path('barang/tambah/', views.tambah_barang, name='tambah_barang'),

    # Edit Barang
    path('barang/edit/<int:id>/', views.edit_barang, name='edit_barang'),

    # Hapus Barang
    path('barang/hapus/<int:id>/', views.hapus_barang, name='hapus_barang'),

    # Import Data Barang
    path(
        'barang/import/',
        views.import_barang,
        name='import_barang'
    ),

    # Export Data Barang
    path(
        'barang/export-excel/',
        views.export_barang_excel,
        name='export_barang_excel'
    ),

    # Download Template Excel
    path(
        'barang/download-template/',
        views.download_template_excel,
        name='download_template_excel'
    ),
]

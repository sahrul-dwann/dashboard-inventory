
from django.contrib import admin
from .models import Barang


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('kode_barang', 'nama_barang', 'kategori', 'stok', 'harga')
    search_fields = ('kode_barang', 'nama_barang')
    list_filter = ('kategori',)

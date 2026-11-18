from django.db import models


class Barang(models.Model):
    kode_barang = models.CharField(max_length=20, unique=True)
    nama_barang = models.CharField(max_length=100)
    kategori = models.CharField(max_length=100)
    stok = models.IntegerField(default=0)
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    deskripsi = models.TextField(blank=True, null=True)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_barang

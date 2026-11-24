
from django import forms
from .models import Barang


class BarangForm(forms.ModelForm):
    class Meta:
        model = Barang
        fields = [
            'kode_barang',
            'nama_barang',
            'kategori',
            'stok',
            'harga',
            'deskripsi',
        ]

        widgets = {
            'kode_barang': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: BRG004',
            }),
            'nama_barang': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama barang',
            }),
            'kategori': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Elektronik',
            }),
            'stok': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan jumlah stok',
                'min': '0',
            }),
            'harga': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan harga barang',
                'min': '0',
                'step': '0.01',
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan deskripsi barang',
                'rows': 4,
            }),
        }


# Form Import Data Barang dari Excel
class ImportBarangForm(forms.Form):
    file = forms.FileField(
        label='Pilih File Excel',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx',
        })
    )

    def clean_file(self):
        file = self.cleaned_data['file']

        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError(
                'Format file harus Excel (.xlsx).'
            )

        return file

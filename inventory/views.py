
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Barang
from .forms import BarangForm


# Dashboard - Menampilkan data barang
def dashboard(request):
    semua_barang = Barang.objects.all()

    search = request.GET.get('search', '')
    kategori_filter = request.GET.get('kategori', '')

    barang = semua_barang

    # Pencarian barang
    if search:
        barang = barang.filter(
            Q(nama_barang__icontains=search) |
            Q(kode_barang__icontains=search)
        )

    # Filter kategori
    if kategori_filter:
        barang = barang.filter(kategori=kategori_filter)

    # Mengurutkan data
    barang = barang.order_by('-tanggal_dibuat')

    # Pagination: 10 barang per halaman
    paginator = Paginator(barang, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Daftar kategori
    kategori_list = (
        semua_barang
        .values_list('kategori', flat=True)
        .distinct()
        .order_by('kategori')
    )

    context = {
        'barang': page_obj,
        'page_obj': page_obj,
        'total_barang': semua_barang.count(),
        'total_stok': sum(item.stok for item in semua_barang),
        'stok_menipis': semua_barang.filter(stok__lte=5).count(),
        'kategori_list': kategori_list,
        'search': search,
        'kategori_filter': kategori_filter,
    }

    return render(request, 'inventory/dashboard.html', context)


# Tambah Barang
def tambah_barang(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil ditambahkan!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Gagal menambahkan barang. Periksa kembali data yang dimasukkan.')

    else:
        form = BarangForm()

    context = {
        'form': form,
    }

    return render(request, 'inventory/tambah_barang.html', context)


# Edit Barang
def edit_barang(request, id):
    barang = get_object_or_404(Barang, id=id)

    if request.method == 'POST':
        form = BarangForm(request.POST, instance=barang)

        if form.is_valid():
            form.save()
            messages.success(request, 'Data barang berhasil diperbarui!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Gagal memperbarui barang. Periksa kembali data yang dimasukkan.')

    else:
        form = BarangForm(instance=barang)

    context = {
        'form': form,
        'barang': barang,
    }

    return render(request, 'inventory/edit_barang.html', context)


# Hapus Barang
def hapus_barang(request, id):
    barang = get_object_or_404(Barang, id=id)

    if request.method == 'POST':
        nama_barang = barang.nama_barang
        barang.delete()

        messages.success(
            request,
            f'Barang "{nama_barang}" berhasil dihapus!'
        )

        return redirect('dashboard')

    context = {
        'barang': barang,
    }

    return render(request, 'inventory/hapus_barang.html', context)

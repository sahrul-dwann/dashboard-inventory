
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Barang
from .forms import BarangForm


# Dashboard - Menampilkan statistik dan grafik barang
def dashboard(request):
    semua_barang = Barang.objects.all()

    # Statistik utama
    total_barang = semua_barang.count()

    total_stok = sum(
        item.stok for item in semua_barang
    )

    # Mengambil daftar barang dengan stok 5 atau kurang
    barang_stok_menipis = list(
        semua_barang
        .filter(stok__lte=5)
        .order_by('stok')
    )

    # Menghitung jumlah barang dengan stok menipis
    stok_menipis = len(barang_stok_menipis)

    # Data grafik berdasarkan kategori
    kategori_chart = list(
        semua_barang
        .values('kategori')
        .annotate(total=Count('id'))
        .order_by('kategori')
    )

    # Data grafik stok barang (maksimal 10 barang)
    stok_chart = list(
        semua_barang
        .order_by('-stok')
        .values('nama_barang', 'stok')[:10]
    )

    context = {
        'total_barang': total_barang,
        'total_stok': total_stok,
        'stok_menipis': stok_menipis,
        'kategori_chart': kategori_chart,
        'stok_chart': stok_chart,
        'barang_stok_menipis': barang_stok_menipis,
    }

    return render(
        request,
        'inventory/dashboard.html',
        context
    )


# Halaman Data Barang
def data_barang(request):
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

    # Pagination
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
        'search': search,
        'kategori_filter': kategori_filter,
        'kategori_list': kategori_list,
    }

    return render(
        request,
        'inventory/data_barang.html',
        context
    )


# Tambah Barang
def tambah_barang(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Barang berhasil ditambahkan!'
            )
            return redirect('dashboard')
        else:
            messages.error(
                request,
                'Gagal menambahkan barang. Periksa kembali data yang dimasukkan.'
            )

    else:
        form = BarangForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'inventory/tambah_barang.html',
        context
    )


# Edit Barang
def edit_barang(request, id):
    barang = get_object_or_404(Barang, id=id)

    if request.method == 'POST':
        form = BarangForm(request.POST, instance=barang)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Data barang berhasil diperbarui!'
            )
            return redirect('dashboard')
        else:
            messages.error(
                request,
                'Gagal memperbarui barang. Periksa kembali data yang dimasukkan.'
            )

    else:
        form = BarangForm(instance=barang)

    context = {
        'form': form,
        'barang': barang,
    }

    return render(
        request,
        'inventory/edit_barang.html',
        context
    )


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

    return render(
        request,
        'inventory/hapus_barang.html',
        context
    )

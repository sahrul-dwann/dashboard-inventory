
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse

from decimal import Decimal, InvalidOperation
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.exceptions import InvalidFileException
from zipfile import BadZipFile

from .models import Barang
from .forms import BarangForm, ImportBarangForm


# Dashboard - Menampilkan statistik dan grafik barang
def dashboard(request):
    semua_barang = Barang.objects.all()

    total_barang = semua_barang.count()

    total_stok = sum(item.stok for item in semua_barang)

    barang_stok_menipis = list(
        semua_barang.filter(stok__lte=5).order_by('stok')
    )

    stok_menipis = len(barang_stok_menipis)

    kategori_chart = list(
        semua_barang
        .values('kategori')
        .annotate(total=Count('id'))
        .order_by('kategori')
    )

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

    return render(request, 'inventory/dashboard.html', context)


# Halaman Data Barang
def data_barang(request):
    semua_barang = Barang.objects.all()

    search = request.GET.get('search', '')
    kategori_filter = request.GET.get('kategori', '')

    barang = semua_barang

    if search:
        barang = barang.filter(
            Q(nama_barang__icontains=search) |
            Q(kode_barang__icontains=search)
        )

    if kategori_filter:
        barang = barang.filter(kategori=kategori_filter)

    barang = barang.order_by('-tanggal_dibuat')

    paginator = Paginator(barang, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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

    return render(request, 'inventory/data_barang.html', context)


# Tambah Barang
def tambah_barang(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil ditambahkan!')
            return redirect('dashboard')
        else:
            messages.error(
                request,
                'Gagal menambahkan barang. Periksa kembali data yang dimasukkan.'
            )
    else:
        form = BarangForm()

    return render(
        request,
        'inventory/tambah_barang.html',
        {'form': form}
    )


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

    return render(
        request,
        'inventory/hapus_barang.html',
        {'barang': barang}
    )


# Export Data Barang ke Excel
def export_barang_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Data Barang'

    headers = [
        'No',
        'Kode Barang',
        'Nama Barang',
        'Kategori',
        'Stok',
        'Harga',
        'Deskripsi',
        'Tanggal Dibuat',
    ]

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(
            start_color='17243A',
            end_color='17243A',
            fill_type='solid'
        )
        cell.alignment = Alignment(horizontal='center')

    semua_barang = Barang.objects.all().order_by('-tanggal_dibuat')

    for no, barang in enumerate(semua_barang, start=1):
        worksheet.append([
            no,
            barang.kode_barang,
            barang.nama_barang,
            barang.kategori,
            barang.stok,
            float(barang.harga),
            barang.deskripsi or '-',
            barang.tanggal_dibuat.strftime('%d-%m-%Y %H:%M'),
        ])

    column_widths = {
        'A': 8,
        'B': 20,
        'C': 30,
        'D': 20,
        'E': 12,
        'F': 18,
        'G': 35,
        'H': 22,
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="data_barang.xlsx"'
    )

    workbook.save(response)

    return response


# Download Template Import Excel
def download_template_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Template Barang'

    headers = [
        'Kode Barang',
        'Nama Barang',
        'Kategori',
        'Stok',
        'Harga',
        'Deskripsi',
    ]

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(
            start_color='17243A',
            end_color='17243A',
            fill_type='solid'
        )
        cell.alignment = Alignment(horizontal='center')

    worksheet.append([
        'BRG001',
        'Laptop',
        'Elektronik',
        10,
        7500000,
        'Laptop kantor',
    ])

    column_widths = {
        'A': 20,
        'B': 30,
        'C': 20,
        'D': 12,
        'E': 18,
        'F': 35,
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="template_import_barang.xlsx"'
    )

    workbook.save(response)

    return response


# Import Data Barang dari Excel
def import_barang(request):
    if request.method == 'POST':
        form = ImportBarangForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            workbook = None

            try:
                workbook = load_workbook(
                    file,
                    read_only=True,
                    data_only=True
                )

                worksheet = workbook.active

                expected_headers = [
                    'Kode Barang',
                    'Nama Barang',
                    'Kategori',
                    'Stok',
                    'Harga',
                    'Deskripsi',
                ]

                actual_headers = [
                    str(cell).strip() if cell is not None else ''
                    for cell in next(
                        worksheet.iter_rows(
                            min_row=1,
                            max_row=1,
                            values_only=True
                        ),
                        ()
                    )
                ]

                if actual_headers != expected_headers:
                    messages.error(
                        request,
                        'Format kolom Excel tidak sesuai template. '
                        'Silakan download template yang tersedia.'
                    )
                    return redirect('import_barang')

                data_barang = []
                errors = []
                kode_dalam_file = set()

                kode_di_database = set(
                    Barang.objects.values_list('kode_barang', flat=True)
                )

                for nomor_baris, row in enumerate(
                    worksheet.iter_rows(min_row=2, values_only=True),
                    start=2
                ):
                    row = list(row[:6])

                    if not any(
                        value is not None and str(value).strip()
                        for value in row
                    ):
                        continue

                    row += [None] * (6 - len(row))

                    kode = str(row[0]).strip() if row[0] is not None else ''
                    nama = str(row[1]).strip() if row[1] is not None else ''
                    kategori = str(row[2]).strip() if row[2] is not None else ''
                    deskripsi = (
                        str(row[5]).strip()
                        if row[5] is not None
                        else ''
                    )

                    if not kode:
                        errors.append(
                            f'Baris {nomor_baris}: Kode barang wajib diisi.'
                        )
                        continue

                    if not nama:
                        errors.append(
                            f'Baris {nomor_baris}: Nama barang wajib diisi.'
                        )
                        continue

                    if not kategori:
                        errors.append(
                            f'Baris {nomor_baris}: Kategori wajib diisi.'
                        )
                        continue

                    if len(kode) > 20:
                        errors.append(
                            f'Baris {nomor_baris}: Kode barang maksimal 20 karakter.'
                        )
                        continue

                    if len(nama) > 100:
                        errors.append(
                            f'Baris {nomor_baris}: Nama barang maksimal 100 karakter.'
                        )
                        continue

                    if len(kategori) > 100:
                        errors.append(
                            f'Baris {nomor_baris}: Kategori maksimal 100 karakter.'
                        )
                        continue

                    if kode in kode_dalam_file:
                        errors.append(
                            f'Baris {nomor_baris}: Kode barang {kode} '
                            'duplikat dalam file Excel.'
                        )
                        continue

                    if kode in kode_di_database:
                        errors.append(
                            f'Baris {nomor_baris}: Kode barang {kode} '
                            'sudah terdaftar di database.'
                        )
                        continue

                    try:
                        stok = Decimal(str(row[3]))

                        if stok != stok.to_integral_value() or stok < 0:
                            raise ValueError

                        stok = int(stok)

                    except (InvalidOperation, ValueError, TypeError):
                        errors.append(
                            f'Baris {nomor_baris}: Stok harus berupa '
                            'bilangan bulat dan tidak boleh negatif.'
                        )
                        continue

                    try:
                        harga = Decimal(str(row[4]))

                        if not harga.is_finite() or harga < 0:
                            raise ValueError

                        if harga.as_tuple().exponent < -2:
                            raise ValueError

                        if harga > Decimal('9999999999.99'):
                            raise ValueError

                    except (InvalidOperation, ValueError, TypeError):
                        errors.append(
                            f'Baris {nomor_baris}: Harga harus berupa '
                            'angka maksimal 2 angka desimal dan tidak boleh negatif.'
                        )
                        continue

                    kode_dalam_file.add(kode)

                    data_barang.append(
                        Barang(
                            kode_barang=kode,
                            nama_barang=nama,
                            kategori=kategori,
                            stok=stok,
                            harga=harga,
                            deskripsi=deskripsi,
                        )
                    )

                if errors:
                    for error in errors[:10]:
                        messages.error(request, error)

                    if len(errors) > 10:
                        messages.error(
                            request,
                            f'Dan {len(errors) - 10} kesalahan lainnya.'
                        )

                    return redirect('import_barang')

                if not data_barang:
                    messages.warning(
                        request,
                        'Tidak ada data barang yang dapat diimpor.'
                    )
                    return redirect('import_barang')

                with transaction.atomic():
                    Barang.objects.bulk_create(data_barang)

                messages.success(
                    request,
                    f'Berhasil mengimpor {len(data_barang)} data barang!'
                )

                return redirect('data_barang')

            except (
                InvalidFileException,
                BadZipFile,
                OSError,
                ValueError,
                KeyError,
                IndexError,
            ):
                messages.error(
                    request,
                    'File Excel tidak valid atau rusak. '
                    'Silakan gunakan template yang tersedia.'
                )
                return redirect('import_barang')

            finally:
                if workbook is not None:
                    workbook.close()

    else:
        form = ImportBarangForm()

    return render(
        request,
        'inventory/import_barang.html',
        {'form': form}
    )

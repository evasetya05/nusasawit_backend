from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SyaratKetentuan, KebijakanPrivasi


def syarat_dan_ketentuan_public(request):
    """Public view for syarat dan ketentuan - accessible by anyone"""
    syarat = get_object_or_404(SyaratKetentuan, is_active=True)
    return render(request, 'syarat_ketentuan/public/syarat_dan_ketentuan.html', {
        'syarat': syarat
    })


def kebijakan_privasi_public(request):
    """Public view for kebijakan privasi - accessible by anyone"""
    kebijakan = get_object_or_404(KebijakanPrivasi, is_active=True)
    return render(request, 'syarat_ketentuan/public/kebijakan_privasi.html', {
        'kebijakan': kebijakan
    })


# Admin views (if needed for dashboard)
def create_syarat_ketentuan(request):
    """Create syarat dan ketentuan (admin only)"""
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    from .forms import SyaratKetentuanForm
    
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    
    if request.method == 'POST':
        form = SyaratKetentuanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Syarat dan ketentuan berhasil dibuat.')
            return redirect('syarat_ketentuan:syarat_ketentuan_list')
    else:
        form = SyaratKetentuanForm()
    
    return render(request, 'syarat_ketentuan/admin/create.html', {'form': form})


def syarat_ketentuan_list(request):
    """List all syarat dan ketentuan (admin only)"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    
    syarat_list = SyaratKetentuan.objects.all()
    return render(request, 'syarat_ketentuan/admin/list.html', {'syarat_list': syarat_list})


def syarat_ketentuan_detail(request, slug):
    """Detail view for syarat dan ketentuan (admin)"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    
    syarat = get_object_or_404(SyaratKetentuan, slug=slug)
    return render(request, 'syarat_ketentuan/admin/detail.html', {'syarat': syarat})
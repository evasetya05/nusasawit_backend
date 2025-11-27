from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from ..forms import UserUpdateForm
from django.contrib.auth.decorators import login_required

User = get_user_model()

class ListUserView(ListView):
    model = User
    template_name = 'user/list-user.html'
    queryset = User.objects.all()
    context_object_name = 'user_list'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EditUserView(UpdateView):
    model = User
    template_name = 'user/edit-user.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('user:list')

@login_required
def user_profile(request, user_id=None):
    """
    View untuk menampilkan dan mengupdate profil pengguna.
    Hanya HR yang dapat melihat profil pengguna lain.
    """
    # Jika user_id tidak diberikan, anggap itu adalah profil pengguna yang sedang login
    if user_id is None:
        user = request.user
    else:
        user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
        else:
            messages.warning(request, 'Terjadi kesalahan saat memperbarui profil Anda.')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'user/update_user_profile.html', {'form': form, 'user': user})

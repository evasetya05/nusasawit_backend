from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.core.models import Employee

from .forms import MessageForm, ThreadStartForm
from .models import ChatMessage, ChatThread


def _get_supervisor_employee(user):
    person = getattr(user, "person", None)
    print(f"  _get_supervisor_employee - Person: {person}")
    if not person:
        print("  _get_supervisor_employee - No person found")
        return None

    # Prefer explicit employee relation
    if hasattr(person, "employee") and person.employee:
        print(f"  _get_supervisor_employee - Found explicit employee: {person.employee}")
        return person.employee

    # Fallback: person and employee share PK
    try:
        employee = Employee.objects.get(pk=person.pk)
        print(f"  _get_supervisor_employee - Found employee by PK: {employee}")
        return employee
    except Employee.DoesNotExist:
        print("  _get_supervisor_employee - No employee found by PK")
        return None


class InboxView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/thread_list.html"

    def get_thread_queryset(self):
        user = self.request.user
        
        # Debug: Print user info
        print(f"=== INBOX VIEW DEBUG ===")
        print(f"User: {user}")
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Is Staff: {user.is_staff}")
        
        # Properly check is_owner
        is_owner_attr = getattr(user, 'is_owner', False)
        is_owner = is_owner_attr() if callable(is_owner_attr) else is_owner_attr
        print(f"Is Owner: {is_owner}")
        
        if user.is_staff or is_owner:
            # Owner/staff can see all threads where they are admin
            print("User is staff/owner - filtering by admin=user")
            queryset = ChatThread.objects.filter(admin=user)
            print(f"Admin threads count: {queryset.count()}")
            return queryset
        
        supervisor = _get_supervisor_employee(user)
        print(f"Supervisor employee found: {supervisor}")
        if supervisor:
            print(f"Supervisor name: {supervisor.name}")
            print(f"Supervisor has subordinates: {supervisor.subordinates.exists()}")
            if supervisor.subordinates.exists():
                # Supervisor can only see their own threads
                print("User is supervisor - filtering by supervisor=supervisor")
                queryset = ChatThread.objects.filter(supervisor=supervisor)
                print(f"Supervisor threads count: {queryset.count()}")
                return queryset
        
        print("User has no access - returning empty queryset")
        return ChatThread.objects.none()

    def get_selected_thread(self, threads):
        thread_id = self.request.GET.get("thread")
        if thread_id:
            try:
                return threads.get(pk=thread_id)
            except ChatThread.DoesNotExist:
                raise Http404("Thread tidak ditemukan")
        return threads.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        threads = (
            self.get_thread_queryset()
            .select_related("admin", "supervisor")
            .prefetch_related(Prefetch("messages", queryset=ChatMessage.objects.select_related("sender_admin", "sender_supervisor")))
            .order_by("-updated_at")
        )

        selected_thread = self.get_selected_thread(threads)

        context.update(
            {
                "threads": threads,
                "selected_thread": selected_thread,
                "message_form": MessageForm(),
                "thread_form": ThreadStartForm(user=self.request.user)
                if (self.request.user.is_staff or (getattr(self.request.user, 'is_owner', False)() if callable(getattr(self.request.user, 'is_owner', None)) else getattr(self.request.user, 'is_owner', False)))
                else None,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "start_thread":
            return self.handle_start_thread(request)
        if action == "send_message":
            return self.handle_send_message(request)

        messages.error(request, "Aksi tidak dikenal.")
        return redirect(reverse("inbox:thread_list"))

    def handle_start_thread(self, request):
        is_owner_attr = getattr(request.user, 'is_owner', False)
        is_owner = is_owner_attr() if callable(is_owner_attr) else is_owner_attr
        
        if not (request.user.is_staff or is_owner):
            messages.error(request, "Hanya admin yang dapat memulai percakapan.")
            return redirect(reverse("inbox:thread_list"))

        form = ThreadStartForm(request.POST, user=request.user)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect(reverse("inbox:thread_list"))

        supervisor = form.cleaned_data["supervisor"]
        subject = form.cleaned_data["subject"] or "Percakapan Baru"

        thread, created = ChatThread.objects.get_or_create(
            admin=request.user,
            supervisor=supervisor,
            defaults={"subject": subject},
        )

        if not created and subject and thread.subject != subject:
            thread.subject = subject
            thread.save(update_fields=["subject", "updated_at"])

        messages.success(request, "Percakapan siap digunakan.")
        return redirect(f"{reverse('inbox:thread_list')}?thread={thread.id}")

    def handle_send_message(self, request):
        thread_id = request.POST.get("thread_id")
        if not thread_id:
            messages.error(request, "Thread tidak ditemukan.")
            return redirect(reverse("inbox:thread_list"))

        try:
            thread = self.get_thread_queryset().get(pk=thread_id)
        except ChatThread.DoesNotExist:
            messages.error(request, "Anda tidak memiliki akses ke percakapan ini.")
            return redirect(reverse("inbox:thread_list"))

        form = MessageForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Pesan tidak boleh kosong.")
            return redirect(f"{reverse('inbox:thread_list')}?thread={thread.id}")

        content = form.cleaned_data["content"]
        message_kwargs = {"thread": thread, "content": content}

        is_owner_attr = getattr(request.user, 'is_owner', False)
        is_owner = is_owner_attr() if callable(is_owner_attr) else is_owner_attr
        
        if request.user.is_staff or is_owner:
            message_kwargs["sender_admin"] = request.user
        else:
            supervisor = _get_supervisor_employee(request.user)
            if not supervisor:
                messages.error(request, "Profil supervisor tidak ditemukan.")
                return redirect(reverse("inbox:thread_list"))
            message_kwargs["sender_supervisor"] = supervisor

        ChatMessage.objects.create(**message_kwargs)
        thread.save(update_fields=["updated_at"])  # touch timestamp
        messages.success(request, "Pesan terkirim.")
        return redirect(f"{reverse('inbox:thread_list')}?thread={thread.id}")

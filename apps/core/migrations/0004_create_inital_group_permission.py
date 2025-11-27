from django.db import migrations


def create_initial_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Owner")
    Group.objects.get_or_create(name="Manager")
    Group.objects.get_or_create(name="Employee")
    Group.objects.get_or_create(name="Consultant")


def remove_initial_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(
        name__in=["Owner", "Manager", "Employee", "Consultant"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_order_paymentreceipt"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_initial_groups, remove_initial_groups),
    ]

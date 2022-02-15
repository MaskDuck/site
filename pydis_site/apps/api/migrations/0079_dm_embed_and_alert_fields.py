# Generated by Django 3.1.14 on 2021-12-19 23:05
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def migrate_filterlist(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    FilterList = apps.get_model("api", "FilterList")
    change_map = {
        "token": True,
        "domain": True,
        "invite": True,
        "extension": False,
        "redirect": False
    }
    for filter_list in FilterList.objects.all():
        filter_list.send_alert = change_map.get(filter_list.name)
        filter_list.dm_embed = ""
        filter_list.save()


def unmigrate_filterlist(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    FilterList = apps.get_model("api", "FilterList")
    for filter_list in FilterList.objects.all():
        filter_list.send_alert = True
        filter_list.server_message_embed = None
        filter_list.save()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0078_merge_20211213_0552'),
        ('api', '0078_merge_20211218_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='send_alert',
            field=models.BooleanField(help_text='Whether alert should be sent.', null=True),
        ),
        migrations.AddField(
            model_name='filter',
            name='dm_embed',
            field=models.CharField(help_text='The content of the DM embed', max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='filterlist',
            name='send_alert',
            field=models.BooleanField(default=True, help_text='Whether alert should be sent.'),
        ),
        migrations.AddField(
            model_name='filterlist',
            name='dm_embed',
            field=models.CharField(help_text='The content of the DM embed', max_length=2000, null=True),
        ),
        migrations.RunPython(migrate_filterlist, unmigrate_filterlist)
    ]

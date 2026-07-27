from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackedroute',
            name='preferred_airlines',
            field=models.CharField(
                blank=True, default='', max_length=100,
                help_text='Comma-separated IATA airline codes, e.g. "EK,AI". Blank = any airline.'),
        ),
        migrations.AddField(
            model_name='trackedroute',
            name='weekends_only',
            field=models.BooleanField(default=False),
        ),
    ]

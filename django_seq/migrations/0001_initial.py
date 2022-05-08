from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(unique=True, verbose_name='key')),
                ('value', models.PositiveBigIntegerField(blank=True, default=0, verbose_name='value')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'sequence',
                'verbose_name_plural': 'sequences',
                'db_table': 'django_seq__sequences',
                'ordering': ['key'],
                'abstract': False,
                'swappable': 'DJANGO_SEQ_SEQUENCE_MODEL',
            },
        ),
    ]

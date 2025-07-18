# Generated by Django 4.2 on 2025-05-16 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_alter_gamematrix_matrix_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player1', models.CharField(max_length=50)),
                ('player2', models.CharField(blank=True, max_length=50, null=True)),
                ('game_code', models.CharField(max_length=6)),
                ('winner', models.CharField(blank=True, max_length=50, null=True)),
                ('board', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'game_history',
            },
        ),
    ]

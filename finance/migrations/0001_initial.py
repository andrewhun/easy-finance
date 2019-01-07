# Generated by Django 2.0.3 on 2018-12-12 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Autovalue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_type', models.CharField(choices=[('Income', 'Income'), ('Expense', 'Expense')], max_length=7)),
                ('title', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('frequency', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], max_length=7)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, max_digits=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(max_length=4)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=100)),
                ('shares', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statement_type', models.CharField(choices=[('Income', 'Income'), ('Expense', 'Expense')], max_length=7)),
                ('title', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(max_length=4)),
                ('stock', models.CharField(max_length=4)),
                ('price', models.DecimalField(decimal_places=2, max_digits=100)),
                ('shares', models.IntegerField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
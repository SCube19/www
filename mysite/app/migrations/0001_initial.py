# Generated by Django 3.2 on 2021-04-26 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('creationDate', models.DateTimeField(auto_now=True)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('creationDate', models.DateTimeField(auto_now=True)),
                ('fileField', models.FileField(upload_to='')),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
                ('directory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file', to='app.directory')),
            ],
        ),
        migrations.CreateModel(
            name='SectionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=50)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=30)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('login', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=30)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatusData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusData', models.CharField(max_length=1000)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
        ),
        migrations.CreateModel(
            name='FileSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('creationDate', models.DateTimeField(auto_now=True)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('validity', models.BooleanField(default=True)),
                ('category', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.sectioncategory')),
                ('fileKey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fsection', to='app.file')),
                ('status', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.status')),
                ('statusData', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.statusdata')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user'),
        ),
        migrations.AddField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user'),
        ),
        migrations.AddField(
            model_name='directory',
            name='parentDirectory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='app.directory'),
        ),
    ]
# Generated by Django 3.2 on 2023-08-02 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('period', models.DurationField()),
                ('doctors', models.ManyToManyField(blank=True, related_name='doctor_exercises', to='api.Doctor')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PatientExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_assigned', models.DateField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_set_exercises', to='api.doctor')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.exercise')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_exercises', to='api.patient')),
            ],
            options={
                'ordering': ['date_assigned', 'exercise__name'],
            },
        ),
        migrations.AddConstraint(
            model_name='patientexercise',
            constraint=models.UniqueConstraint(fields=('patient', 'exercise'), name='Patient-Exercise'),
        ),
    ]
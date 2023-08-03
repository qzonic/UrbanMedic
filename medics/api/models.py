from django.db import models


class PatientDoctorBaseModel(models.Model):
    """ Abstract model for patient and doctor. """

    first_name = models.CharField(
        max_length=64,
    )
    last_name = models.CharField(
        max_length=64,
    )

    class Meta:
        abstract = True
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Patient(PatientDoctorBaseModel):
    """ Patient model. """
    pass


class Doctor(PatientDoctorBaseModel):
    """ Doctor model. """
    pass


class Exercise(models.Model):
    """ Exercise model. """

    name = models.CharField(
        max_length=128,
        unique=True,
    )
    period = models.DurationField()
    doctors = models.ManyToManyField(
        to=Doctor,
        blank=True,
        related_name='doctor_exercises',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class PatientExercise(models.Model):
    """ Model for patient exercise. """

    patient = models.ForeignKey(
        to=Patient,
        on_delete=models.CASCADE,
        related_name='patient_exercises'
    )
    doctor = models.ForeignKey(
        to=Doctor,
        on_delete=models.CASCADE,
        related_name='doctor_set_exercises',
    )
    exercise = models.ForeignKey(
        to=Exercise,
        on_delete=models.CASCADE,
    )
    date_assigned = models.DateField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['date_assigned', 'exercise__name']
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'exercise'],
                name='Patient-Exercise'
            )
        ]

    def __str__(self):
        return f'{self.patient} | {self.doctor} | {self.exercise}'

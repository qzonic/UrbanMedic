from django.contrib import admin

from .models import Doctor, Exercise, Patient, PatientExercise


class PatientDoctorBaseAdminModel(admin.ModelAdmin):
    """ Base patient and doctor admin model. """

    list_display = (
        'first_name',
        'last_name',
    )
    search_fields = (
        'first_name',
        'last_name',
    )


class DoctorAdmin(PatientDoctorBaseAdminModel):
    """ Doctor admin model. """
    pass


class PatientAdmin(PatientDoctorBaseAdminModel):
    """ Patient admin model. """
    pass


class ExerciseAdmin(admin.ModelAdmin):
    """ Exercise admin model. """

    list_display = (
        'name',
        'period',
        'get_doctors',
    )
    search_fields = (
        'name',
    )

    @admin.display(description='Doctors count', empty_value='-')
    def get_doctors(self, obj):
        return obj.doctors.count()


class PatientExerciseAdmin(admin.ModelAdmin):
    """ PatientExercise admin model. """

    list_display = (
        'patient',
        'doctor',
        'exercise',
        'date_assigned',
    )


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(PatientExercise, PatientExerciseAdmin)

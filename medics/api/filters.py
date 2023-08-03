from django_filters import filterset

from .models import PatientExercise


class PatientExerciseFilterSet(filterset.FilterSet):
    """ Filter for patient exercises by period. """

    date = filterset.DateFilter(method='get_patient_exercises_by_period')

    class Meta:
        model = PatientExercise
        fields = (
            'date',
        )

    def get_patient_exercises_by_period(self, queryset, name, value):
        relevant_exercises = []
        for patient_exercise in queryset:
            if patient_exercise.date_assigned <= value:
                days = (value - patient_exercise.date_assigned).days
                if days % patient_exercise.exercise.period.days == 0:
                    relevant_exercises.append(patient_exercise.id)
        return PatientExercise.objects.filter(id__in=relevant_exercises)

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Doctor, Patient, Exercise, PatientExercise
from .filters import PatientExerciseFilterSet
from .serializers import (
    DoctorSerializer,
    PatientShortSerializer,
    PatientFullSerializer,
    ExerciseFullReadSerializer,
    ExerciseShortReadSerializer,
    ExerciseWriteSerializer,
    PatientExerciseWriteSerializer,
    PatientExerciseReadSerializer
)


class DoctorViewSet(viewsets.ModelViewSet):
    """ Viewset for create, read, update delete doctors. """

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """ Viewset for create, read, update delete patient. """

    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientShortSerializer
        return PatientFullSerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    """ Viewset for create, read, update delete patient """

    queryset = Exercise.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['doctors__id']

    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseShortReadSerializer
        elif self.action == 'retrieve':
            return ExerciseFullReadSerializer
        return ExerciseWriteSerializer


class PatientExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset for patient exercises. """

    queryset = PatientExercise.objects.all()
    serializer_class = PatientExerciseReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PatientExerciseFilterSet

    def get_patient(self):
        return get_object_or_404(Patient, pk=self.kwargs.get('patient_id'))

    def get_queryset(self):
        return PatientExercise.objects.filter(patient=self.get_patient())


class DoctorExerciseViewSet(viewsets.ModelViewSet):
    """ Viewset for list, retrieve, create and delete doctor exercises. """

    queryset = PatientExercise.objects.all()
    serializer_class = PatientExerciseWriteSerializer

    def get_doctor(self):
        return get_object_or_404(Doctor, pk=self.kwargs.get('doctor_id'))

    def get_queryset(self):
        return PatientExercise.objects.filter(doctor=self.get_doctor())

    def perform_create(self, serializer):
        serializer.save(doctor=self.get_doctor())

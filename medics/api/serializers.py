from django.db.transaction import atomic
from rest_framework import serializers, status

from .models import Doctor, Exercise, Patient, PatientExercise


class DoctorSerializer(serializers.ModelSerializer):
    """ Serializer for doctor model. """

    class Meta:
        model = Doctor
        fields = (
            'id',
            'first_name',
            'last_name',
        )
        read_only_fields = (
            'id',
        )


class BaseExerciseSerializer(serializers.ModelSerializer):
    """ Base serializer for exercise. """

    class Meta:
        model = Exercise
        fields = (
            'id',
            'name',
            'period',
            'doctors',
        )
        read_only_fields = (
            'id',
        )


class ExerciseWriteSerializer(BaseExerciseSerializer):
    """ Serializer for write exercise. """

    doctors = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        many=True,
    )

    @atomic
    def create(self, validated_data):
        doctors = validated_data.pop('doctors')
        exercise = super().create(validated_data)
        exercise.doctors.set(doctors)
        return exercise

    @atomic
    def update(self, instance, validated_data):
        if 'doctors' in validated_data:
            doctors = validated_data.pop('doctors')
            instance.doctors.clear()
            instance.doctors.set(doctors)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ExerciseFullReadSerializer(instance).data


class ExerciseFullReadSerializer(BaseExerciseSerializer):
    """ Serializer for read exercise (full). """

    doctors = DoctorSerializer(many=True)


class ExerciseShortReadSerializer(serializers.ModelSerializer):
    """ Serializer for read exercises (short). """

    class Meta:
        model = Exercise
        fields = (
            'id',
            'name',
            'period',
        )


class PatientFullSerializer(serializers.ModelSerializer):
    """ Serializer for patient model with maximum info. """

    exercises = ExerciseShortReadSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'first_name',
            'last_name',
            'exercises',
        )
        read_only_fields = (
            'id',
            'exercises',
        )


class PatientShortSerializer(serializers.ModelSerializer):
    """ Serializer for patient model with minimum info. """

    class Meta:
        model = Patient
        fields = (
            'id',
            'first_name',
            'last_name',
        )


class PatientExerciseReadSerializer(serializers.ModelSerializer):
    """ Serializer for read patient exercises. """

    doctor = DoctorSerializer(read_only=True)
    exercise = ExerciseShortReadSerializer(read_only=True)

    class Meta:
        model = PatientExercise
        fields = (
            'id',
            'doctor',
            'exercise',
            'date_assigned',
        )


class PatientExerciseWriteSerializer(serializers.ModelSerializer):
    """ Serializer for write patient exercise. """

    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all()
    )
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all()
    )

    class Meta:
        model = PatientExercise
        fields = (
            'patient',
            'exercise',
        )

    def validate(self, attrs):
        doctor = self.context['view'].kwargs.get('doctor_id')
        patient = attrs.get('patient')
        exercise = attrs.get('exercise')
        if not exercise.doctors.filter(id=doctor).exists():
            raise serializers.ValidationError(
                {'doctor': 'Этот доктор не может назначить это упражнение!'},
                status.HTTP_400_BAD_REQUEST
            )
        elif PatientExercise.objects.filter(patient=patient, exercise=exercise).exists():
            raise serializers.ValidationError(
                {'patient': 'Этому пациенту уже назначили это упражнение!'},
                status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def to_representation(self, instance):
        return DoctorExerciseSerializer(instance).data


class DoctorExerciseSerializer(serializers.ModelSerializer):
    """ Serializer for doctor set exercises. """

    patient = PatientShortSerializer()
    exercise = ExerciseShortReadSerializer()

    class Meta:
        model = PatientExercise
        fields = (
            'id',
            'patient',
            'exercise',
            'date_assigned',
        )

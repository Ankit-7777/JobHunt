from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Recruiter, Job, Employee, Application
import re
from decimal import Decimal


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']

class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'confirm_password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"
        
        if password != confirm_password:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        
        if not re.match(pattern, password):
            raise serializers.ValidationError("Password must contain at least eight characters with a digit, an uppercase letter, and a lowercase letter.")
        
        return data

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data) 
        if validated_data['role'] == 'recruiter':
            Recruiter.objects.create(user=user) 
        elif validated_data['role'] == 'employee':
            Employee.objects.create(user=user) 

        return user

class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ['id', 'company_name', 'user']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'phone_number', 'user']

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'salary']
        read_only_fields = ['recruiter']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        
        try:
            recruiter = Recruiter.objects.get(user=user)
        except Recruiter.DoesNotExist:
            raise serializers.ValidationError("Recruiter profile not found.")

        validated_data['recruiter'] = recruiter
        return super().create(validated_data)

    def validate_salary(self, value):
        if not isinstance(value, Decimal):
            raise serializers.ValidationError("Salary must be a decimal value.")
        return value

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id',
            'employee',
            'job',
            'cover_letter',
            'submitted_at',
            'status',
            'is_active'
        ]
        read_only_fields = ['id', 'employee', 'submitted_at', 'status', 'is_active']

    
    def validate_job(self, value):
        """
        Validate that the job exists and is active.
        """
        if not value.is_active:
            raise serializers.ValidationError("The selected job is not active.")
        return value

    def validate_cover_letter(self, value):
        """
        Validate the cover letter. Ensure it's not too long if provided.
        """
        if value and len(value) > 1000:
            raise serializers.ValidationError("Cover letter must be under 1000 characters.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if not hasattr(request.user, 'employee'):
            raise serializers.ValidationError("User does not have an associated employee.")
        validated_data['employee'] = request.user.employee
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.job = validated_data.get('job', instance.job)
        instance.cover_letter = validated_data.get('cover_letter', instance.cover_letter)
        instance.status = validated_data.get('status', instance.status)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
    

    

from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from .models import User, Recruiter, Job, Employee, Application
from .serializers import SignupSerializer, UserProfileSerializer, RecruiterSerializer, JobSerializer, EmployeeSerializer, ApplicationSerializer
from .utils import get_tokens_for_user
from .pagination import MyPageNumberPagination
from  .permissions import IsRecruiterOrSuperadmin, IsEmployeeRecruiterOrSuperadmin
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

class UserAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        action = request.query_params.get('action')
        if action == 'register':
            return self.signup(request)
        elif action == 'login':
            return self.login(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            # send_welcome_email.delay(user.email, user.first_name, user.role)
            token = get_tokens_for_user(user)
            
            return Response({
                'message': 'Registration successful',
                'token': token,
                'user_data': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            token = get_tokens_for_user(user)

            return Response({
                'message': 'Login successful',
                'token': token,
                'user_data': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsRecruiterOrSuperadmin]
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == 'recruiter':
            recruiter = Recruiter.objects.get(user=user)
            return Job.objects.filter(recruiter=recruiter)
        if user.is_superuser:
            return Job.objects.all()
        return Job.objects.none() 
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "Job List retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            recruiter = Recruiter.objects.get(user=user)
        except Recruiter.DoesNotExist:
            return Response({"error": "Recruiter profile not found."}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = request.data.copy()
        validated_data['recruiter'] = recruiter

        serializer = self.get_serializer(data=validated_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Job retrieved successfully.",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Job updated successfully.",
            "data": serializer.data
        })

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Job partially updated successfully.",
            "data": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Job deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployeeRecruiterOrSuperadmin]
    pagination_class = MyPageNumberPagination


    def get_queryset(self):
        user = self.request.user
        if user.role == 'employee':
            return self.queryset.filter(employee__user=user)
        elif user.role == 'recruiter':
            recruiter = get_object_or_404(Recruiter, user=user)
            return self.queryset.filter(job__recruiter=recruiter)
        return self.queryset


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Application created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "Applications List retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Application retrieved successfully.",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Application updated successfully.",
            "data": serializer.data
        })

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Application partially updated successfully.",
            "data": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Application deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT) 
    




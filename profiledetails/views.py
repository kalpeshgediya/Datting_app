from django.shortcuts import render
from profiledetails.models import *
from profiledetails.serializers import *
from profiledetails.utils import *
# Create your views here.
from time import timezone
from django.shortcuts import render
import requests
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from knox.views import LoginView as KnoxLoginView
from rest_framework.views import APIView
from django.db.models import Q,Sum,Count
from knox.auth import TokenAuthentication
from django.contrib.auth import login
from rest_framework.response import Response
# from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.models import AuthToken
from django.shortcuts import get_object_or_404
# import datetime
# from datetime import date, timedelta,datetime
import json
from django.http import HttpResponse
from django.conf import settings

from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework import viewsets
import pyotp
import base64

User = get_user_model()
# Create your views here.
class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'response': serializer.data,
            'scucess': True,
            'message': 'User created successfully',
            'status': status.HTTP_201_CREATED,})

def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or 
    passed phone number as argument.
    """
    if phone:
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)
        link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=7c59cf94-d129-11ec-9c12-0200cd936042&to={phone}&from=MMBook&templatename=mymedbook&var1={otp_key}&var2={otp_key}'
        result = requests.get(link, verify=False)
        return otp_key
    else:
        return False


class ValidatePhoneSendOTP(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            phone_number = request.data.get('phone')
            if phone_number:
                phone = str(phone_number)
                user = User.objects.filter(phone=phone)
                if user.exists():
                    data = user.first()
                    old_otp = data.otp
                    new_otp = send_otp(phone)
                    if old_otp:
                        data.otp = new_otp
                        data.save()
                        print(data.otp,'-------2-----')
                        return Response({'message': 'OTP sent successfully','status': status.HTTP_200_OK})
                    else:
                        data.otp = new_otp
                        data.save()
                        print(data.otp,'-------1-----')
                        return Response({'message': 'OTP sent successfully','status': status.HTTP_200_OK})
                else:
                    return Response({'message': 'User not found ! please register','status': status.HTTP_404_NOT_FOUND,})
            else:
                return Response({'message': 'Phone number is required','status': status.HTTP_400_BAD_REQUEST,})
        except Exception as e:
            return Response({'message': str(e),'status': status.HTTP_400_BAD_REQUEST,})

# verify otp
class VerifyPhoneOTPView(APIView):
    def post(self, request, format=None):
        try:
            phone = request.data.get('phone')
            otp = request.data.get('otp')
            print(phone, otp)
            if phone and otp:
                user = User.objects.filter(phone=phone)
                if user.exists():
                    user = user.first()
                    if user.otp == otp:
                        login(request, user)
                        return Response({
                            'status': True,
                            'details': 'Login Successfully',
                            'token': AuthToken.objects.create(user)[1],
                            'response': {
                                'id': user.id,
                                'phone': user.phone,
                                'otp': user.otp,}})
                    else:
                        return Response({'message': 'OTP does not match'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Phone or OTP is missing'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'status': False,'message': str(e),'details': 'Login Failed'})

# logout api view
# class LogoutView(APIView):
#     # permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [IsAuthenticated,]

#     def post(self, request, format=None):
#         try:
#             request.user.auth_token.delete()
#             return Response({'message': 'Logout successfully','status': status.HTTP_200_OK,})
#         except Exception as e:
#             return Response({'message': str(e),'status': status.HTTP_400_BAD_REQUEST,})
        
class User_get_view(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = User_get_serializer
    queryset = User.objects.all()
    lookup_field = "id"
    
    def list(self, request, *args, **kwargs):
        queryset=User.objects.get(id=request.user.id)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class User_get_view(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = User_get_serializer
    queryset = User.objects.all()
    lookup_field = "id"
    
    def list(self, request, *args, **kwargs):
        queryset=User.objects.get(id=request.user.id)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class User_update_view(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = User_get_serializer
    queryset = User.objects.all()
    lookup_field = "id"
    
    def update(self, request, *args, **kwargs):
        name = request.data.get('name')
        gender = request.data.get('gender')
        gender_intersted_in = request.data.get('gender_intersted_in')
        looking_for = request.data.get('looking_for')
        interest_in = request.data.get('interest_in')
        sexual_orientation_in = request.data.get('sexual_orientation_in')
        user_dob = request.data.get('user_dob')
        pick_prompt = request.data.get('pick_prompt')
        relationship_type = request.data.get('relationship_type')
        work_title = request.data.get('work_title')
        company_industry_name = request.data.get('company_industry_name')
        university = request.data.get('university')
        Height = request.data.get('Height')
        language_you_know = request.data.get('language_you_know')
        zodia_choices = request.data.get('zodia_choices')
        drinking_choices = request.data.get('drinking_choices')
        smoking_choices = request.data.get('smoking_choices')
        education_choices = request.data.get('education_choices')
        status_choices = request.data.get('status_choices')
        dietary_choices = request.data.get('dietary_choices')
        work_out = request.data.get('work_out')
        
        queryset=User.objects.get(id=request.user.id)
        queryset.name = name
        queryset.gender = gender
        queryset.gender_intersted_in = gender_intersted_in
        queryset.looking_for= looking_for
        queryset.interest_in = interest_in
        queryset.sexual_orientation_in = sexual_orientation_in
        queryset.user_dob = user_dob
        queryset.pick_prompt=pick_prompt
        queryset.relationship_type=relationship_type
        queryset.work_title=work_title
        queryset.company_industry_name=company_industry_name
        queryset.university=university
        queryset.Height=Height
        queryset.language_you_know=language_you_know
        queryset.zodia_choices=zodia_choices
        queryset.drinking_choices=drinking_choices
        queryset.smoking_choices=smoking_choices
        queryset.education_choices=education_choices
        queryset.status_choices=status_choices
        queryset.dietary_choices=dietary_choices
        queryset.work_out=work_out
        queryset.save()
        return Response({"message":"User data update Successfully"},status=status.HTTP_200_OK)
    
    
    
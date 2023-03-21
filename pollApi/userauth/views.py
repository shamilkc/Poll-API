from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    #creating user with a username and password
    if User.objects.filter(username=request.data['username']).exists():
        return Response({"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        username=request.data['username'],
        password=request.data['password']
    )

    refresh_token = RefreshToken.for_user(user=user)
    return Response(
        {"message": "User created successfully", "refresh": str(refresh_token), "access":str(refresh_token.access_token)
        }, 
    status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, pk):
    #updating user
    user = User.objects.get(username=str(pk))
    if request.user == user:
        user.username = request.data.get('username', user.username)
        user.set_password(request.data.get('password', user.password))
        user.save()
        return Response({"message": "User updated successfully"})
    else:
        return Response({"message": "Not allowed"})



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    #login a user and returning the token
    username = request.data['username']
    password = request.data['password']
    
    user = authenticate(username=username, password=password)
    print(user)
    if user:
        refresh_token = RefreshToken.for_user(user=user)
        return Response({"message": "logged successfully", "refresh": str(refresh_token), "access":str(refresh_token.access_token)
        },)
    else:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)




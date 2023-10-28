from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer, UserSearchSerializer, FriendRequestSerializer, PendingRequestsSerializer
from django.contrib.auth.models import User
from django.db.models import Q,F
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest
from rest_framework.throttling import UserRateThrottle

class UserSignupView(APIView):
    """
    API endpoint for user registration.

    This view allows users to register by providing their information via a POST request.
    
    Request:
    - HTTP Method: POST
    - Data Parameters (in JSON format):
        - username (str): The desired username for the new user.
        - email (str): The email address of the new user.
        - password (str): The password for the new user.
    
    Response:
    - HTTP 201 Created: If the registration is successful.
        Returns a JSON response with a success message.
    - HTTP 400 Bad Request: If the provided data is invalid or there are errors.
        Returns a JSON response with details of the validation errors.

    Example Usage:
    ```
    POST /api/signup/
    {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "secure_password"
    }
    ```
    Note:
    - Make sure to include the 'Content-Type: application/json' header in your request.
    - Passwords should be securely hashed before saving in database.
    """
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = User.objects.filter(email=email).first()
            if user is None or not user.check_password(password):
                return Response({'success':'false','message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                })
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserSearchView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        search_keyword = self.request.query_params.get('search')
        if search_keyword:
            return User.objects.filter(Q(email__iexact=search_keyword) | Q(username__icontains=search_keyword))
        return User.objects.none()

class FriendRequestCreateView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            sender = request.user
            recipient_id = request.data.get('receiver')
            recipient_id = User.objects.get(pk=recipient_id)

            # Check if a friend request from the sender to the recipient already exists
            if FriendRequest.objects.filter(sender=sender, receiver=recipient_id, status='Pending').exists():
                return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new friend request
            friend_request = FriendRequest(sender=sender, receiver=recipient_id, status='Pending')
            friend_request.save()
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({'success':'false','message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({'success':'false','message': 'An error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FriendRequestAcceptView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(pk=request_id)

            if request.user != friend_request.receiver:
                return Response({'detail': 'You do not have permission to accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)

            friend_request.status = 'Accepted'
            friend_request.save()
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data)
        except Http404:
            return Response({'success':'false','message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success':'false','message': 'An error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FriendRequestRejectView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(pk=request_id)

            if request.user != friend_request.receiver:
                return Response({'detail': 'You do not have permission to reject this friend request.'}, status=status.HTTP_403_FORBIDDEN)

            friend_request.status = 'Rejected'
            friend_request.save()
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data)
        except Http404:
            return Response({'success':'false','message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success':'false','message': 'An error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AcceptedFriendsView(ListAPIView):
    serializer_class = PendingRequestsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # Query for accepted requests
        accepted_friendships = FriendRequest.objects.filter(sender=user, status='Accepted')
        return accepted_friendships
        

class PendingFriendsView(ListAPIView):
    serializer_class = PendingRequestsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # Query for pending requests
        pending_friendships = FriendRequest.objects.filter(sender=user, status='Pending')
        return pending_friendships
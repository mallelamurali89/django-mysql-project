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

class FriendRequestAcceptView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, request_id):
        friend_request = FriendRequest.objects.get(pk=request_id)

        if request.user != friend_request.receiver:
            return Response({'detail': 'You do not have permission to accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.status = 'Accepted'
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

class FriendRequestRejectView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, request_id):
        friend_request = FriendRequest.objects.get(pk=request_id)

        if request.user != friend_request.receiver:
            return Response({'detail': 'You do not have permission to reject this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.status = 'Rejected'
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

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
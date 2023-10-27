from django.urls import path
from .views import UserSignupView, UserLoginView, UserSearchView, FriendRequestCreateView, FriendRequestAcceptView, FriendRequestRejectView, AcceptedFriendsView, PendingFriendsView 

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/', UserSearchView.as_view(), name='search'),
    path('request-create/', FriendRequestCreateView.as_view(), name='request_create'),
    path('request-accept/<int:request_id>/', FriendRequestAcceptView.as_view(), name='friend-request-accept'),
    path('request-reject/<int:request_id>/', FriendRequestRejectView.as_view(), name='friend-request-reject'),
    path('accepted-friends/', AcceptedFriendsView.as_view(), name='friends-accepted'),
    path('pending-friends/', PendingFriendsView.as_view(), name='friends-pending'),
]

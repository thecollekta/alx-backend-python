# messaging_app/chats/permissions.py

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the conversation/message.
        if hasattr(obj, "sender") and obj.sender == request.user:
            return True
        if hasattr(obj, "participants") and request.user in obj.participants.all():
            return True
        return False


class IsParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a conversation to view it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user in obj.participants.all()

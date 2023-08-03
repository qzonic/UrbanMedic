from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           GenericViewSet):
    """ Viewset for create and delete object. """
    pass

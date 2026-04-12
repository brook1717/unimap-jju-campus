from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class RouteView(APIView):
    """
    GET /api/routes/?start=<id>&end=<id>
    Returns the shortest walking path between two campus locations.
    Implementation deferred to Week 2 (services.py).
    """

    def get(self, request):
        return Response(
            {'detail': 'Routing engine not yet implemented.'},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

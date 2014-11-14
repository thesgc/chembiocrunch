from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from qpcr.models import QPCRWorkflow
from qpcr.serializers import QPCRWorkflowSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@api_view(['GET', 'POST'])
def workflow_list(request):
    """
    List all qpcrworkflow, or create a new qpcrworkflow.
    """
    if request.method == 'GET':
        workflows = QPCRWorkflow.objects.get_user_records(request.user)
        serializer = QPCRWorkflowSerializer(workflows, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = QPCRWorkflowSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.object.created_by = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def workflow_detail(request, id):
    """
    List all qpcrworkflow, or create a new qpcrworkflow.
    """
    if request.method == 'GET':
        workflows = QPCRWorkflow.objects.get_user_records(request.user)
        serializer = QPCRWorkflowSerializer(workflows.get(pk=id))
        return Response(serializer.data)

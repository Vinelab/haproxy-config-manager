from rest_framework.decorators import api_view
from django.http import HttpResponse
import HAProxyManager


@api_view(['GET'])
def add(request):
    if request.method == 'GET':

        instance_id = str(request.GET.get('instance_id'))
        backend = str(request.GET.get('backend'))
        private_ip = str(request.GET.get('private_ip'))
        port_numb = str(request.GET.get('port_numb'))

        proxy = HAProxyManager.HAProxyManager()
        proxy.add_server(backend, instance_id, private_ip, port_numb)

        return HttpResponse(200)


@api_view(['GET'])
def remove(request):
    if request.method == 'GET':

        instance_id = str(request.GET.get('instance_id'))
        private_ip = str(request.GET.get('private_ip'))
        port_numb = str(request.GET.get('port_numb'))

        proxy = HAProxyManager.HAProxyManager()
        proxy.remove_server(instance_id, private_ip, port_numb)

        return HttpResponse(200)


@api_view(['GET'])
def reloadproxy(request):
    if request.method == 'GET':
        proxy = HAProxyManager.HAProxyManager()
        proxy.reload_haproxy()


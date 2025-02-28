from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ModeloIA, DocumentoTreinamento

@require_http_methods(["GET"])
def api_status(request):
    """
    Endpoint para verificar o status da API e da chave de API.
    """
    return JsonResponse({
        'status': 'online',
        'api_key': {
            'nivel_acesso': request.api_key.get_nivel_acesso_display(),
            'total_requisicoes': request.api_key.total_requisicoes
        }
    })

@require_http_methods(["GET"])
def listar_modelos(request):
    """
    Endpoint para listar os modelos de IA disponíveis.
    """
    modelos = ModeloIA.objects.filter(status='treinado').values(
        'id', 'nome', 'tipo', 'versao', 'data_ultimo_treinamento'
    )
    
    return JsonResponse({
        'modelos': list(modelos)
    })

@require_http_methods(["GET"])
def listar_documentos(request):
    """
    Endpoint para listar os documentos de treinamento.
    Requer nível de acesso 'training'.
    """
    if request.api_key.nivel_acesso != 'training':
        return JsonResponse({
            'error': 'Acesso negado',
            'message': 'Esta operação requer nível de acesso de treinamento'
        }, status=403)
    
    documentos = DocumentoTreinamento.objects.values(
        'id', 'titulo', 'tipo', 'status', 'data_upload', 'data_processamento'
    )
    
    return JsonResponse({
        'documentos': list(documentos)
    }) 
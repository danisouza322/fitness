from django.http import JsonResponse
from django.urls import resolve
from .models import APIKey

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se é uma rota da API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Obter a chave da API do cabeçalho
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return JsonResponse({
                'error': 'API Key não fornecida',
                'message': 'Por favor, forneça uma API Key válida no cabeçalho X-API-Key'
            }, status=401)
        
        try:
            # Buscar e validar a chave
            key = APIKey.objects.get(chave=api_key, ativo=True)
            
            # Verificar o nível de acesso
            url_name = resolve(request.path_info).url_name
            method = request.method
            
            # Definir permissões baseadas no nível de acesso
            if key.nivel_acesso == 'read' and method not in ['GET', 'HEAD', 'OPTIONS']:
                return JsonResponse({
                    'error': 'Acesso negado',
                    'message': 'Esta chave de API tem permissão apenas para leitura'
                }, status=403)
            
            elif key.nivel_acesso == 'write' and url_name.startswith('training_'):
                return JsonResponse({
                    'error': 'Acesso negado',
                    'message': 'Esta chave de API não tem permissão para operações de treinamento'
                }, status=403)
            
            # Incrementar contador de requisições
            key.incrementar_requisicoes()
            
            # Adicionar informações da chave ao request para uso nas views
            request.api_key = key
            
            return self.get_response(request)
            
        except APIKey.DoesNotExist:
            return JsonResponse({
                'error': 'API Key inválida',
                'message': 'A API Key fornecida não é válida ou está inativa'
            }, status=401) 
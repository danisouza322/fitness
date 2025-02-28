from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import (
    DietaSugerida, DietaFeedback, ConfiguracaoIA, 
    LogTreinamentoIA, User, DocumentoTreinamento,
    ModeloIA, APIKey
)
import PyPDF2
import json
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.conf import settings
import os

@staff_member_required
def ia_dashboard(request):
    # Estatísticas gerais
    total_dietas = DietaSugerida.objects.count()
    media_satisfacao = DietaFeedback.objects.filter(satisfacao__isnull=False).aggregate(Avg('satisfacao'))['satisfacao__avg'] or 0
    taxa_aderencia = DietaFeedback.objects.filter(aderencia__isnull=False).aggregate(Avg('aderencia'))['aderencia__avg'] or 0
    
    # Usuários ativos no último mês
    mes_passado = timezone.now() - timedelta(days=30)
    usuarios_ativos = User.objects.filter(last_login__gte=mes_passado).count()
    
    # Dados de performance dos últimos 30 dias
    dados_performance = []
    for i in range(30):
        data = timezone.now() - timedelta(days=i)
        feedback_dia = DietaFeedback.objects.filter(
            data_feedback__date=data.date()
        )
        media_satisfacao_dia = feedback_dia.aggregate(Avg('satisfacao'))['satisfacao__avg'] or 0
        media_aderencia_dia = feedback_dia.aggregate(Avg('aderencia'))['aderencia__avg'] or 0
        dados_performance.append({
            'data': data.strftime('%d/%m'),
            'satisfacao': round(media_satisfacao_dia, 2),
            'aderencia': round(media_aderencia_dia, 2)
        })
    
    # Últimos logs
    ultimos_logs = LogTreinamentoIA.objects.order_by('-data_hora')[:10]
    
    context = {
        'total_dietas': total_dietas,
        'media_satisfacao': round(media_satisfacao, 2),
        'taxa_aderencia': round(taxa_aderencia, 2),
        'usuarios_ativos': usuarios_ativos,
        'dados_performance': dados_performance,
        'ultimos_logs': ultimos_logs,
    }
    
    return render(request, 'admin/ia/dashboard.html', context)

@staff_member_required
def treinamento_dashboard(request):
    documentos = DocumentoTreinamento.objects.all().order_by('-data_upload')
    modelos = ModeloIA.objects.all().order_by('-data_criacao')
    api_keys = APIKey.objects.all().order_by('-data_criacao')
    
    context = {
        'documentos': documentos,
        'modelos': modelos,
        'api_keys': api_keys,
    }
    
    return render(request, 'admin/ia/treinamento/dashboard.html', context)

@staff_member_required
@require_POST
def upload_documento(request):
    try:
        titulo = request.POST.get('titulo')
        tipo = request.POST.get('tipo')
        arquivo = request.FILES.get('arquivo')
        
        if not all([titulo, tipo, arquivo]):
            return JsonResponse({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        # Criar diretório para documentos se não existir
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'documentos_treinamento')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salvar arquivo
        nome_arquivo = f"{uuid.uuid4()}_{arquivo.name}"
        caminho_arquivo = os.path.join(upload_dir, nome_arquivo)
        
        with default_storage.open(caminho_arquivo, 'wb+') as destino:
            for chunk in arquivo.chunks():
                destino.write(chunk)
        
        # Criar documento no banco
        documento = DocumentoTreinamento.objects.create(
            titulo=titulo,
            tipo=tipo,
            arquivo=f"documentos_treinamento/{nome_arquivo}",
            status='pendente'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Documento enviado com sucesso',
            'doc_id': documento.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao enviar documento: {str(e)}'
        })

@staff_member_required
@require_POST
def criar_modelo(request):
    try:
        nome = request.POST.get('nome')
        tipo = request.POST.get('tipo_modelo')
        versao = request.POST.get('versao')
        parametros = request.POST.get('parametros')
        
        if not all([nome, tipo, versao, parametros]):
            return JsonResponse({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        try:
            parametros_json = json.loads(parametros)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Parâmetros JSON inválidos'})
        
        modelo = ModeloIA.objects.create(
            nome=nome,
            tipo=tipo,
            versao=versao,
            parametros=parametros_json,
            status='nao_treinado'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Modelo criado com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao criar modelo: {str(e)}'
        })

@staff_member_required
@require_POST
def gerar_api_key(request):
    try:
        nivel_acesso = request.POST.get('nivel_acesso')
        if not nivel_acesso:
            return JsonResponse({'success': False, 'message': 'Nível de acesso é obrigatório'})
        
        key = APIKey.objects.create(
            key=uuid.uuid4().hex,
            nivel_acesso=nivel_acesso,
            ativo=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Chave de API gerada com sucesso',
            'key': key.key
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao gerar chave de API: {str(e)}'
        })

@staff_member_required
@require_POST
def processar_documento(request, doc_id):
    documento = get_object_or_404(DocumentoTreinamento, id=doc_id)
    
    try:
        if documento.status != 'pendente':
            return JsonResponse({
                'success': False,
                'message': 'Documento já foi processado ou está em processamento'
            })
        
        documento.status = 'processando'
        documento.save()
        
        # Extrair texto do documento
        texto_extraido = ''
        caminho_arquivo = os.path.join(settings.MEDIA_ROOT, documento.arquivo.name)
        
        if documento.tipo == 'PDF':
            with open(caminho_arquivo, 'rb') as arquivo:
                leitor_pdf = PyPDF2.PdfReader(arquivo)
                for pagina in leitor_pdf.pages:
                    texto_extraido += pagina.extract_text()
        elif documento.tipo in ['TXT', 'CSV']:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                texto_extraido = arquivo.read()
        elif documento.tipo == 'JSON':
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados_json = json.load(arquivo)
                texto_extraido = json.dumps(dados_json, ensure_ascii=False, indent=2)
        
        # Salvar texto extraído
        documento.texto_extraido = texto_extraido
        documento.status = 'processado'
        documento.save()
        
        LogTreinamentoIA.objects.create(
            tipo='processamento_documento',
            status='sucesso',
            mensagem=f'Documento {documento.titulo} processado com sucesso'
        )
        
        return JsonResponse({
            'success': True,
            'status': 'processado',
            'message': 'Documento processado com sucesso'
        })
        
    except Exception as e:
        documento.status = 'erro'
        documento.save()
        
        LogTreinamentoIA.objects.create(
            tipo='processamento_documento',
            status='erro',
            mensagem=f'Erro ao processar documento {documento.titulo}: {str(e)}'
        )
        
        return JsonResponse({
            'success': False,
            'status': 'erro',
            'message': f'Erro ao processar documento: {str(e)}'
        })

@staff_member_required
@require_POST
def treinar_modelo(request, modelo_id):
    modelo = get_object_or_404(ModeloIA, id=modelo_id)
    
    try:
        if modelo.status == 'treinando':
            return JsonResponse({
                'success': False,
                'message': 'Modelo já está em treinamento'
            })
        
        modelo.status = 'treinando'
        modelo.save()
        
        # Aqui você implementaria a lógica de treinamento do modelo
        # Por enquanto, vamos apenas simular o início do treinamento
        
        LogTreinamentoIA.objects.create(
            tipo='treinamento_modelo',
            status='iniciado',
            mensagem=f'Treinamento do modelo {modelo.nome} iniciado'
        )
        
        return JsonResponse({
            'success': True,
            'status': 'treinando',
            'message': 'Treinamento iniciado com sucesso'
        })
        
    except Exception as e:
        modelo.status = 'erro'
        modelo.save()
        
        LogTreinamentoIA.objects.create(
            tipo='treinamento_modelo',
            status='erro',
            mensagem=f'Erro ao treinar modelo {modelo.nome}: {str(e)}'
        )
        
        return JsonResponse({
            'success': False,
            'status': 'erro',
            'message': f'Erro ao iniciar treinamento: {str(e)}'
        })

@staff_member_required
@require_POST
def revogar_api_key(request, key):
    api_key = get_object_or_404(APIKey, key=key)
    
    try:
        api_key.ativo = False
        api_key.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Chave de API revogada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao revogar chave de API: {str(e)}'
        })

def extrair_texto_pdf(arquivo):
    """Extrai texto de um arquivo PDF"""
    pdf_reader = PyPDF2.PdfReader(arquivo)
    texto = ""
    
    for pagina in pdf_reader.pages:
        texto += pagina.extract_text() + "\n"
    
    return texto 
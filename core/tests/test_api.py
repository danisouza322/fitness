from django.test import TestCase, Client
from django.urls import reverse
from core.models import APIKey, ModeloIA, DocumentoTreinamento
import uuid

class APITestCase(TestCase):
    def setUp(self):
        # Criar chaves de API para teste
        self.api_key_read = APIKey.objects.create(
            chave=uuid.uuid4().hex,
            nivel_acesso='read',
            ativo=True
        )
        
        self.api_key_write = APIKey.objects.create(
            chave=uuid.uuid4().hex,
            nivel_acesso='write',
            ativo=True
        )
        
        self.api_key_training = APIKey.objects.create(
            chave=uuid.uuid4().hex,
            nivel_acesso='training',
            ativo=True
        )
        
        self.api_key_inactive = APIKey.objects.create(
            chave=uuid.uuid4().hex,
            nivel_acesso='read',
            ativo=False
        )
        
        # Criar cliente de teste
        self.client = Client()
        
        # Criar alguns modelos de teste
        self.modelo = ModeloIA.objects.create(
            nome='Modelo Teste',
            tipo='nutricao',
            versao='1.0',
            parametros={'param1': 'valor1'},
            status='treinado'
        )
        
        # Criar alguns documentos de teste
        self.documento = DocumentoTreinamento.objects.create(
            titulo='Documento Teste',
            tipo='PDF',
            arquivo='test.pdf',
            status='processado'
        )
    
    def test_api_sem_chave(self):
        """Testa acesso à API sem chave"""
        response = self.client.get(reverse('api:api_status'))
        self.assertEqual(response.status_code, 401)
    
    def test_api_chave_inativa(self):
        """Testa acesso à API com chave inativa"""
        response = self.client.get(
            reverse('api:api_status'),
            HTTP_X_API_KEY=self.api_key_inactive.chave
        )
        self.assertEqual(response.status_code, 401)
    
    def test_api_status(self):
        """Testa endpoint de status da API"""
        response = self.client.get(
            reverse('api:api_status'),
            HTTP_X_API_KEY=self.api_key_read.chave
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'online')
    
    def test_listar_modelos(self):
        """Testa listagem de modelos"""
        response = self.client.get(
            reverse('api:api_listar_modelos'),
            HTTP_X_API_KEY=self.api_key_read.chave
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['modelos']), 1)
    
    def test_listar_documentos_sem_permissao(self):
        """Testa listagem de documentos sem permissão adequada"""
        response = self.client.get(
            reverse('api:api_listar_documentos'),
            HTTP_X_API_KEY=self.api_key_read.chave
        )
        self.assertEqual(response.status_code, 403)
    
    def test_listar_documentos_com_permissao(self):
        """Testa listagem de documentos com permissão adequada"""
        response = self.client.get(
            reverse('api:api_listar_documentos'),
            HTTP_X_API_KEY=self.api_key_training.chave
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['documentos']), 1)
    
    def test_incremento_requisicoes(self):
        """Testa se o contador de requisições é incrementado"""
        key = self.api_key_read
        requisicoes_iniciais = key.total_requisicoes
        
        self.client.get(
            reverse('api:api_status'),
            HTTP_X_API_KEY=key.chave
        )
        
        key.refresh_from_db()
        self.assertEqual(key.total_requisicoes, requisicoes_iniciais + 1)
    
    def test_restricao_metodo_read(self):
        """Testa restrição de método para chave de leitura"""
        response = self.client.post(
            reverse('api:api_status'),
            HTTP_X_API_KEY=self.api_key_read.chave
        )
        self.assertEqual(response.status_code, 403) 
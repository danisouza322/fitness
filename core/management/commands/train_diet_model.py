from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.ml_models.diet_model import DietRecommender
from core.ml_models.utils import preparar_dados_treino, avaliar_modelo
import os
from django.conf import settings
import random

class Command(BaseCommand):
    help = 'Treina o modelo de recomendação de dietas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=100,
            help='Número de épocas de treinamento'
        )
        parser.add_argument(
            '--test-split',
            type=float,
            default=0.2,
            help='Proporção dos dados para teste (0-1)'
        )

    def handle(self, *args, **options):
        # Criar diretório para modelos se não existir
        models_dir = os.path.join(settings.BASE_DIR, 'media', 'ml_models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Inicializar modelo
        modelo = DietRecommender()
        
        # Coletar dados de todos os usuários
        todos_dados = []
        for user in User.objects.all():
            dados_usuario = preparar_dados_treino(user)
            todos_dados.extend(dados_usuario)
        
        if not todos_dados:
            self.stdout.write(
                self.style.WARNING('Nenhum dado de treinamento encontrado!')
            )
            return
        
        # Embaralhar dados
        random.shuffle(todos_dados)
        
        # Dividir em treino e teste
        split_idx = int(len(todos_dados) * (1 - options['test_split']))
        dados_treino = todos_dados[:split_idx]
        dados_teste = todos_dados[split_idx:]
        
        self.stdout.write(
            f'Dados de treino: {len(dados_treino)}, Dados de teste: {len(dados_teste)}'
        )
        
        # Treinar modelo
        for epoch in range(options['epochs']):
            random.shuffle(dados_treino)  # embaralhar a cada época
            modelo.treinar(dados_treino)
            
            if (epoch + 1) % 10 == 0:  # avaliar a cada 10 épocas
                metricas = avaliar_modelo(modelo, dados_teste)
                self.stdout.write(
                    f'Época {epoch + 1}: MSE={metricas["mse"]:.4f}, '
                    f'MAE={metricas["mae"]:.4f}, RMSE={metricas["rmse"]:.4f}'
                )
        
        # Avaliar modelo final
        metricas_finais = avaliar_modelo(modelo, dados_teste)
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTreinamento concluído!\n'
                f'Métricas finais:\n'
                f'MSE: {metricas_finais["mse"]:.4f}\n'
                f'MAE: {metricas_finais["mae"]:.4f}\n'
                f'RMSE: {metricas_finais["rmse"]:.4f}'
            )
        )
        
        # Salvar modelo
        modelo_path = os.path.join(models_dir, 'diet_recommender.pth')
        modelo.salvar_modelo(modelo_path)
        self.stdout.write(
            self.style.SUCCESS(f'Modelo salvo em: {modelo_path}')
        ) 
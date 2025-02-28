import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Tuple
from decimal import Decimal

class DietRecommenderNet(nn.Module):
    def __init__(self, num_features: int, hidden_size: int = 64):
        super(DietRecommenderNet, self).__init__()
        
        # Camadas da rede neural
        self.layers = nn.Sequential(
            nn.Linear(num_features, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)

class DietRecommender:
    def __init__(self):
        self.feature_names = [
            'calorias_normalized',
            'proteinas_normalized',
            'gorduras_normalized',
            'carboidratos_normalized',
            'satisfacao_media',
            'aderencia_media',
            'preferencia_usuario',
            'restricao_usuario',
            'horario_refeicao'
        ]
        
        self.model = DietRecommenderNet(len(self.feature_names))
        self.optimizer = optim.Adam(self.model.parameters())
        self.criterion = nn.BCELoss()
        
        # Estatísticas para normalização
        self.stats = {
            'calorias': {'min': 0, 'max': 1000},
            'proteinas': {'min': 0, 'max': 100},
            'gorduras': {'min': 0, 'max': 100},
            'carboidratos': {'min': 0, 'max': 100}
        }
    
    def _normalize_features(self, alimento: Dict, feedback_stats: Dict, 
                          preferencias: Dict, horario: int) -> torch.Tensor:
        """Normaliza as características do alimento para input do modelo"""
        features = []
        
        # Normalização dos macronutrientes
        features.append((alimento['calorias'] - self.stats['calorias']['min']) / 
                       (self.stats['calorias']['max'] - self.stats['calorias']['min']))
        
        features.append((alimento['proteinas'] - self.stats['proteinas']['min']) / 
                       (self.stats['proteinas']['max'] - self.stats['proteinas']['min']))
        
        features.append((alimento['gorduras'] - self.stats['gorduras']['min']) / 
                       (self.stats['gorduras']['max'] - self.stats['gorduras']['min']))
        
        features.append((alimento['carboidratos'] - self.stats['carboidratos']['min']) / 
                       (self.stats['carboidratos']['max'] - self.stats['carboidratos']['min']))
        
        # Feedback histórico
        features.append(feedback_stats.get('satisfacao_media', 0.5))
        features.append(feedback_stats.get('aderencia_media', 0.5))
        
        # Preferências do usuário
        features.append(1.0 if preferencias.get('preferido', False) else 0.0)
        features.append(1.0 if preferencias.get('restrito', False) else 0.0)
        
        # Horário da refeição (normalizado para 0-1)
        features.append(horario / 24.0)
        
        return torch.tensor(features, dtype=torch.float32)
    
    def treinar(self, dados_treino: List[Tuple[Dict, Dict, Dict, int, float]]):
        """Treina o modelo com dados históricos"""
        self.model.train()
        
        for alimento, feedback, preferencias, horario, target in dados_treino:
            self.optimizer.zero_grad()
            
            # Prepara os dados
            x = self._normalize_features(alimento, feedback, preferencias, horario)
            y = torch.tensor([target], dtype=torch.float32)
            
            # Forward pass
            output = self.model(x)
            loss = self.criterion(output, y)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
    
    def prever_score(self, alimento: Dict, feedback_stats: Dict, 
                     preferencias: Dict, horario: int) -> float:
        """Prevê o score para um alimento específico"""
        self.model.eval()
        with torch.no_grad():
            x = self._normalize_features(alimento, feedback_stats, preferencias, horario)
            score = self.model(x).item()
            return score
    
    def salvar_modelo(self, caminho: str):
        """Salva o modelo treinado"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'stats': self.stats
        }, caminho)
    
    def carregar_modelo(self, caminho: str):
        """Carrega um modelo previamente treinado"""
        checkpoint = torch.load(caminho)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.stats = checkpoint['stats'] 
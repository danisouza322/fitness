from typing import List, Dict, Tuple
from ..models import Alimento, DietaFeedback, AlimentoPersonalizado
from django.db.models import Avg
from django.contrib.auth.models import User
import numpy as np
from datetime import datetime

def preparar_dados_treino(user: User) -> List[Tuple[Dict, Dict, Dict, int, float]]:
    """Prepara dados de treino a partir do histórico do usuário"""
    dados_treino = []
    
    # Buscar feedbacks do usuário
    feedbacks = DietaFeedback.objects.filter(usuario=user)
    
    # Buscar preferências do usuário
    preferencias = {
        ap.nome.lower(): {'preferido': ap.tipo == 'P', 'restrito': ap.tipo == 'R'}
        for ap in AlimentoPersonalizado.objects.filter(usuario=user)
    }
    
    # Para cada alimento que já foi incluído em dietas do usuário
    for alimento in Alimento.objects.all():
        # Estatísticas de feedback para este alimento
        stats_feedback = feedbacks.filter(
            dieta__cafe_manha=alimento
        ).aggregate(
            satisfacao_media=Avg('satisfacao'),
            aderencia_media=Avg('aderencia')
        )
        
        if not stats_feedback['satisfacao_media']:
            stats_feedback = feedbacks.filter(
                dieta__almoco=alimento
            ).aggregate(
                satisfacao_media=Avg('satisfacao'),
                aderencia_media=Avg('aderencia')
            )
        
        if not stats_feedback['satisfacao_media']:
            stats_feedback = feedbacks.filter(
                dieta__jantar=alimento
            ).aggregate(
                satisfacao_media=Avg('satisfacao'),
                aderencia_media=Avg('aderencia')
            )
        
        if not stats_feedback['satisfacao_media']:
            stats_feedback = feedbacks.filter(
                dieta__lanche=alimento
            ).aggregate(
                satisfacao_media=Avg('satisfacao'),
                aderencia_media=Avg('aderencia')
            )
        
        # Se não há feedback, usar valores neutros
        if not stats_feedback['satisfacao_media']:
            stats_feedback = {
                'satisfacao_media': 3.0,
                'aderencia_media': 2.0
            }
        
        # Normalizar valores de feedback
        stats_feedback = {
            'satisfacao_media': float(stats_feedback['satisfacao_media']) / 5.0,
            'aderencia_media': float(stats_feedback['aderencia_media']) / 3.0
        }
        
        # Dados do alimento
        dados_alimento = {
            'calorias': float(alimento.calorias),
            'proteinas': float(alimento.proteinas),
            'gorduras': float(alimento.gorduras),
            'carboidratos': float(alimento.carboidratos)
        }
        
        # Preferências do usuário para este alimento
        pref_alimento = preferencias.get(alimento.nome.lower(), {
            'preferido': False,
            'restrito': False
        })
        
        # Gerar exemplos para diferentes horários
        for hora in [7, 12, 19, 16]:  # café, almoço, jantar, lanche
            # Target (score alvo) baseado em preferências e feedback
            target = 0.5  # valor base
            
            if pref_alimento['preferido']:
                target += 0.3
            elif pref_alimento['restrito']:
                target = 0.0
            else:
                target += (stats_feedback['satisfacao_media'] - 0.5) * 0.4
                target += (stats_feedback['aderencia_media'] - 0.5) * 0.2
            
            # Ajustar target com base no horário e categoria do alimento
            if (hora == 7 and alimento.categoria == 'C') or \
               (hora == 12 and alimento.categoria == 'A') or \
               (hora == 19 and alimento.categoria == 'J') or \
               (hora == 16 and alimento.categoria == 'L'):
                target += 0.1
            
            target = max(0.0, min(1.0, target))  # garantir que está entre 0 e 1
            
            dados_treino.append((
                dados_alimento,
                stats_feedback,
                pref_alimento,
                hora,
                target
            ))
    
    return dados_treino

def avaliar_modelo(modelo, dados_teste: List[Tuple[Dict, Dict, Dict, int, float]]) -> Dict:
    """Avalia o desempenho do modelo"""
    predictions = []
    targets = []
    
    for alimento, feedback, preferencias, horario, target in dados_teste:
        pred = modelo.prever_score(alimento, feedback, preferencias, horario)
        predictions.append(pred)
        targets.append(target)
    
    predictions = np.array(predictions)
    targets = np.array(targets)
    
    mse = np.mean((predictions - targets) ** 2)
    mae = np.mean(np.abs(predictions - targets))
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'rmse': float(np.sqrt(mse))
    } 
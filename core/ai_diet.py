from decimal import Decimal
from typing import List, Dict
from .models import (
    Alimento, DietaFeedback, AlimentoPersonalizado,
    ConfiguracaoIA, LogTreinamentoIA
)

class DietaAI:
    def __init__(self, usuario):
        self.usuario = usuario
        self.alimentos_personalizados = AlimentoPersonalizado.objects.filter(usuario=usuario)
        self.feedbacks = DietaFeedback.objects.filter(usuario=usuario).order_by('-data_feedback')
        
        # Carregar configuração ativa
        self.config = ConfiguracaoIA.objects.filter(ativa=True).first()
        if not self.config:
            # Usar valores padrão se não houver configuração ativa
            self.config = ConfiguracaoIA(
                nome="Padrão",
                score_base=5.0,
                peso_feedback=0.5,
                bonus_preferido=2.0,
                ajuste_porcao_min=0.5,
                ajuste_porcao_max=2.0,
                dist_calorias_cafe=0.25,
                dist_calorias_almoco=0.35,
                dist_calorias_jantar=0.35,
                dist_calorias_lanche=0.05
            )
    
    def registrar_log(self, tipo: str, status: str, mensagem: str, dados: dict = None):
        """Registra um log de operação da IA"""
        LogTreinamentoIA.objects.create(
            tipo=tipo,
            status=status,
            configuracao=self.config if self.config.id else None,
            usuario=self.usuario,
            mensagem=mensagem,
            dados=dados
        )
    
    def calcular_score_alimento(self, alimento: Alimento) -> float:
        """Calcula um score para cada alimento baseado nas preferências e feedback do usuário"""
        score = self.config.score_base
        
        # Verificar alimentos personalizados do usuário
        alimento_personalizado = self.alimentos_personalizados.filter(nome__iexact=alimento.nome).first()
        if alimento_personalizado:
            if alimento_personalizado.tipo == 'R':  # Alimento restrito
                self.registrar_log(
                    'G', 'A',
                    f'Alimento {alimento.nome} ignorado por restrição do usuário'
                )
                return 0.0
            elif alimento_personalizado.tipo == 'P':  # Alimento preferido
                score += self.config.bonus_preferido
                self.registrar_log(
                    'G', 'S',
                    f'Bônus aplicado ao alimento {alimento.nome} por preferência do usuário'
                )
        
        # Analisar feedback histórico
        alimento_feedbacks = self.feedbacks.filter(
            dieta__cafe_manha=alimento
        ).union(
            self.feedbacks.filter(dieta__almoco=alimento)
        ).union(
            self.feedbacks.filter(dieta__jantar=alimento)
        ).union(
            self.feedbacks.filter(dieta__lanche=alimento)
        )
        
        if alimento_feedbacks.exists():
            avg_satisfacao = sum(f.satisfacao for f in alimento_feedbacks) / alimento_feedbacks.count()
            ajuste_feedback = (avg_satisfacao - 3) * self.config.peso_feedback
            score += ajuste_feedback
            
            self.registrar_log(
                'G', 'S',
                f'Score do alimento {alimento.nome} ajustado em {ajuste_feedback:.2f} baseado em feedback',
                {
                    'alimento': alimento.nome,
                    'score_original': self.config.score_base,
                    'ajuste_feedback': ajuste_feedback,
                    'score_final': score
                }
            )
        
        return max(0.0, min(10.0, score))
    
    def selecionar_alimentos_refeicao(self, categoria: str, calorias_alvo: Decimal) -> List[Alimento]:
        """Seleciona alimentos para uma refeição baseado nas preferências e feedback"""
        alimentos = Alimento.objects.filter(categoria=categoria)
        alimentos_scores = [
            (alimento, self.calcular_score_alimento(alimento))
            for alimento in alimentos
        ]
        
        # Ordenar por score e filtrar alimentos com score > 0
        alimentos_validos = [(a, s) for a, s in alimentos_scores if s > 0]
        alimentos_validos.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar os melhores alimentos que se encaixam nas calorias alvo
        selecionados = []
        calorias_total = Decimal('0')
        
        for alimento, score in alimentos_validos[:4]:  # Tentar com os 4 melhores
            if calorias_total + Decimal(str(alimento.calorias)) <= calorias_alvo:
                selecionados.append(alimento)
                calorias_total += Decimal(str(alimento.calorias))
                
                self.registrar_log(
                    'G', 'S',
                    f'Alimento {alimento.nome} selecionado para {categoria} com score {score:.2f}'
                )
        
        return selecionados
    
    def ajustar_porcoes(self, alimentos: List[Alimento], calorias_alvo: Decimal) -> List[Dict]:
        """Ajusta as porções dos alimentos para atingir o alvo calórico"""
        if not alimentos:
            return []
        
        calorias_total = sum(a.calorias for a in alimentos)
        if calorias_total == 0:
            return []
        
        fator_ajuste = calorias_alvo / Decimal(str(calorias_total))
        fator_ajuste = min(
            max(fator_ajuste, Decimal(str(self.config.ajuste_porcao_min))),
            Decimal(str(self.config.ajuste_porcao_max))
        )
        
        self.registrar_log(
            'G', 'S',
            f'Porções ajustadas com fator {fator_ajuste:.2f}',
            {
                'calorias_alvo': float(calorias_alvo),
                'calorias_original': float(calorias_total),
                'fator_ajuste': float(fator_ajuste)
            }
        )
        
        return [
            {
                'alimento': alimento,
                'porcao_ajustada': alimento.porcao * fator_ajuste
            }
            for alimento in alimentos
        ] 
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

class PerfilUsuario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    NIVEL_ATIVIDADE_CHOICES = [
        ('S', 'Sedentário'),
        ('L', 'Levemente ativo'),
        ('M', 'Moderadamente ativo'),
        ('V', 'Muito ativo'),
        ('E', 'Extra ativo'),
    ]
    
    OBJETIVO_CHOICES = [
        ('P', 'Perder peso'),
        ('M', 'Manter peso'),
        ('G', 'Ganhar peso'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    idade = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    altura = models.PositiveIntegerField(help_text="Altura em centímetros")
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso em kg")
    nivel_atividade = models.CharField(max_length=1, choices=NIVEL_ATIVIDADE_CHOICES)
    objetivo = models.CharField(max_length=1, choices=OBJETIVO_CHOICES)
    
    def calcular_bmr(self):
        peso = float(self.peso)
        if self.genero == 'M':
            return Decimal(str(66 + (13.7 * peso) + (5 * self.altura) - (6.8 * self.idade)))
        else:
            return Decimal(str(655 + (9.6 * peso) + (1.8 * self.altura) - (4.7 * self.idade)))
    
    def fator_atividade(self):
        fatores = {
            'S': Decimal('1.2'),
            'L': Decimal('1.375'),
            'M': Decimal('1.55'),
            'V': Decimal('1.725'),
            'E': Decimal('1.9')
        }
        return fatores[self.nivel_atividade]
    
    def calcular_tdee(self):
        bmr = self.calcular_bmr()
        tdee = bmr * self.fator_atividade()
        
        if self.objetivo == 'P':
            return tdee - Decimal('500')
        elif self.objetivo == 'G':
            return tdee + Decimal('500')
        return tdee
    
    def calcular_macronutrientes(self):
        tdee = self.calcular_tdee()
        
        # Proteína: 0.8g por kg de peso corporal
        proteina = self.peso * Decimal('0.8')  # self.peso já é Decimal
        
        # Gordura: 25% das calorias totais
        gordura = (tdee * Decimal('0.25')) / Decimal('9')  # 9 calorias por grama de gordura
        
        # Carboidratos: restante das calorias
        calorias_restantes = tdee - (proteina * Decimal('4')) - (gordura * Decimal('9'))  # 4 calorias por grama de proteína
        carboidratos = calorias_restantes / Decimal('4')  # 4 calorias por grama de carboidrato
        
        return {
            'proteina': round(float(proteina), 1),
            'gordura': round(float(gordura), 1),
            'carboidratos': round(float(carboidratos), 1)
        }

class Alimento(models.Model):
    CATEGORIA_CHOICES = [
        ('C', 'Café da manhã'),
        ('A', 'Almoço'),
        ('J', 'Jantar'),
        ('L', 'Lanche'),
    ]
    
    nome = models.CharField(max_length=100)
    calorias = models.PositiveIntegerField()
    proteinas = models.DecimalField(max_digits=5, decimal_places=2)
    gorduras = models.DecimalField(max_digits=5, decimal_places=2)
    carboidratos = models.DecimalField(max_digits=5, decimal_places=2)
    categoria = models.CharField(max_length=1, choices=CATEGORIA_CHOICES)
    porcao = models.DecimalField(max_digits=8, decimal_places=2, help_text="Porção em gramas")
    
    def __str__(self):
        return self.nome

class DietaSugerida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    cafe_manha = models.ManyToManyField(Alimento, related_name='dietas_cafe')
    almoco = models.ManyToManyField(Alimento, related_name='dietas_almoco')
    jantar = models.ManyToManyField(Alimento, related_name='dietas_jantar')
    lanche = models.ManyToManyField(Alimento, related_name='dietas_lanche')
    
    def calcular_totais(self):
        todas_refeicoes = list(self.cafe_manha.all()) + list(self.almoco.all()) + \
                         list(self.jantar.all()) + list(self.lanche.all())
        
        return {
            'calorias': sum(a.calorias for a in todas_refeicoes),
            'proteinas': sum(float(a.proteinas) for a in todas_refeicoes),
            'gorduras': sum(float(a.gorduras) for a in todas_refeicoes),
            'carboidratos': sum(float(a.carboidratos) for a in todas_refeicoes)
        }

class DietaFeedback(models.Model):
    SATISFACAO_CHOICES = [
        (1, 'Muito Insatisfeito'),
        (2, 'Insatisfeito'),
        (3, 'Neutro'),
        (4, 'Satisfeito'),
        (5, 'Muito Satisfeito')
    ]
    
    ADERENCIA_CHOICES = [
        (1, 'Não Segui'),
        (2, 'Segui Parcialmente'),
        (3, 'Segui Totalmente')
    ]
    
    dieta = models.ForeignKey(DietaSugerida, on_delete=models.CASCADE, related_name='feedbacks')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    satisfacao = models.IntegerField(choices=SATISFACAO_CHOICES)
    aderencia = models.IntegerField(choices=ADERENCIA_CHOICES)
    comentarios = models.TextField(blank=True)
    data_feedback = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Feedback de Dieta'
        verbose_name_plural = 'Feedbacks de Dietas'
        ordering = ['-data_feedback']

class AlimentoPersonalizado(models.Model):
    TIPO_CHOICES = [
        ('P', 'Preferido'),
        ('R', 'Restrito')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alimentos_personalizados')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    motivo = models.TextField(blank=True, help_text="Motivo da restrição ou preferência")
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Alimento Personalizado'
        verbose_name_plural = 'Alimentos Personalizados'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class ConfiguracaoIA(models.Model):
    nome = models.CharField(max_length=100)
    ativa = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Parâmetros de Score
    peso_feedback = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Peso do feedback do usuário no cálculo do score (0-1)"
    )
    score_base = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Score base para alimentos sem histórico"
    )
    bonus_preferido = models.FloatField(
        default=2.0,
        help_text="Bônus no score para alimentos preferidos"
    )
    
    # Parâmetros de Ajuste de Porções
    ajuste_porcao_min = models.FloatField(
        default=0.5,
        help_text="Fator mínimo para ajuste de porção"
    )
    ajuste_porcao_max = models.FloatField(
        default=2.0,
        help_text="Fator máximo para ajuste de porção"
    )
    
    # Distribuição de Calorias
    dist_calorias_cafe = models.FloatField(
        default=0.25,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Proporção de calorias para o café da manhã"
    )
    dist_calorias_almoco = models.FloatField(
        default=0.35,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Proporção de calorias para o almoço"
    )
    dist_calorias_jantar = models.FloatField(
        default=0.35,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Proporção de calorias para o jantar"
    )
    dist_calorias_lanche = models.FloatField(
        default=0.05,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Proporção de calorias para lanches"
    )
    
    class Meta:
        verbose_name = "Configuração da IA"
        verbose_name_plural = "Configurações da IA"
    
    def __str__(self):
        return f"{self.nome} ({'Ativa' if self.ativa else 'Inativa'})"
    
    def save(self, *args, **kwargs):
        # Garantir que apenas uma configuração esteja ativa
        if self.ativa:
            ConfiguracaoIA.objects.exclude(pk=self.pk).update(ativa=False)
        super().save(*args, **kwargs)

class LogTreinamentoIA(models.Model):
    TIPO_CHOICES = [
        ('G', 'Geração de Dieta'),
        ('F', 'Feedback'),
        ('A', 'Ajuste de Parâmetros')
    ]
    
    STATUS_CHOICES = [
        ('S', 'Sucesso'),
        ('E', 'Erro'),
        ('A', 'Alerta')
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    data = models.DateTimeField(auto_now_add=True)
    configuracao = models.ForeignKey(ConfiguracaoIA, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensagem = models.TextField()
    dados = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Log de Treinamento"
        verbose_name_plural = "Logs de Treinamento"
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.data.strftime('%d/%m/%Y %H:%M')}"

class Assinatura(models.Model):
    PLANO_CHOICES = [
        ('B', 'Básico'),
        ('P', 'Premium'),
        ('E', 'Enterprise')
    ]
    
    STATUS_CHOICES = [
        ('A', 'Ativa'),
        ('I', 'Inativa'),
        ('P', 'Pendente'),
        ('C', 'Cancelada')
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    plano = models.CharField(max_length=1, choices=PLANO_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_plano_display()}"

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aprovado'),
        ('R', 'Recusado'),
        ('C', 'Cancelado')
    ]
    
    assinatura = models.ForeignKey(Assinatura, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    codigo_transacao = models.CharField(max_length=100, null=True, blank=True)
    detalhes = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.assinatura.usuario.username} - R$ {self.valor} - {self.get_status_display()}"

class DocumentoTreinamento(models.Model):
    TIPO_CHOICES = [
        ('PDF', 'PDF'),
        ('TXT', 'TXT'),
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('processado', 'Processado'),
        ('erro', 'Erro'),
    ]
    
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    arquivo = models.FileField(upload_to='documentos_treinamento/')
    texto_extraido = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_upload = models.DateTimeField(auto_now_add=True)
    data_processamento = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.titulo} ({self.tipo})"
    
    class Meta:
        verbose_name = 'Documento de Treinamento'
        verbose_name_plural = 'Documentos de Treinamento'

class ModeloIA(models.Model):
    TIPO_CHOICES = [
        ('nutricao', 'Nutrição'),
        ('exercicios', 'Exercícios'),
        ('suplementacao', 'Suplementação'),
    ]
    
    STATUS_CHOICES = [
        ('nao_treinado', 'Não Treinado'),
        ('treinando', 'Treinando'),
        ('treinado', 'Treinado'),
        ('erro', 'Erro'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    versao = models.CharField(max_length=50)
    parametros = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nao_treinado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultimo_treinamento = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nome} v{self.versao}"
    
    class Meta:
        verbose_name = 'Modelo de IA'
        verbose_name_plural = 'Modelos de IA'

class APIKey(models.Model):
    NIVEL_ACESSO_CHOICES = [
        ('read', 'Somente Leitura'),
        ('write', 'Leitura e Escrita'),
        ('training', 'Treinamento'),
    ]
    
    chave = models.CharField(max_length=64, unique=True)
    nivel_acesso = models.CharField(max_length=10, choices=NIVEL_ACESSO_CHOICES)
    ativo = models.BooleanField(default=True)
    total_requisicoes = models.IntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_requisicao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.chave} ({self.get_nivel_acesso_display()})"
    
    def incrementar_requisicoes(self):
        self.total_requisicoes += 1
        self.data_ultima_requisicao = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = 'Chave de API'
        verbose_name_plural = 'Chaves de API'

from django.contrib import admin
from .models import (
    PerfilUsuario, Alimento, DietaSugerida, DietaFeedback, 
    AlimentoPersonalizado, ConfiguracaoIA, LogTreinamentoIA,
    Assinatura, Pagamento, DocumentoTreinamento, ModeloIA, APIKey
)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'idade', 'genero', 'altura', 'peso', 'nivel_atividade', 'objetivo')
    list_filter = ('genero', 'nivel_atividade', 'objetivo')
    search_fields = ('usuario__username',)

@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'calorias', 'proteinas', 'gorduras', 'carboidratos', 'porcao')
    list_filter = ('categoria',)
    search_fields = ('nome',)

@admin.register(DietaSugerida)
class DietaSugeridaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('usuario__username',)

@admin.register(DietaFeedback)
class DietaFeedbackAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'dieta', 'satisfacao', 'aderencia', 'data_feedback')
    list_filter = ('satisfacao', 'aderencia', 'data_feedback')
    search_fields = ('usuario__username', 'comentarios')
    readonly_fields = ('data_feedback',)

@admin.register(AlimentoPersonalizado)
class AlimentoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'tipo', 'data_adicao')
    list_filter = ('tipo', 'data_adicao')
    search_fields = ('nome', 'usuario__username', 'motivo')
    readonly_fields = ('data_adicao',)

@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa', 'data_atualizacao')
    list_filter = ('ativa', 'data_criacao', 'data_atualizacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativa')
        }),
        ('Parâmetros de Score', {
            'fields': ('peso_feedback', 'score_base', 'bonus_preferido')
        }),
        ('Ajuste de Porções', {
            'fields': ('ajuste_porcao_min', 'ajuste_porcao_max')
        }),
        ('Distribuição de Calorias', {
            'fields': (
                'dist_calorias_cafe', 'dist_calorias_almoco',
                'dist_calorias_jantar', 'dist_calorias_lanche'
            )
        })
    )

@admin.register(LogTreinamentoIA)
class LogTreinamentoIAAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'status', 'data', 'usuario', 'mensagem')
    list_filter = ('tipo', 'status', 'data', 'configuracao')
    search_fields = ('mensagem', 'usuario__username')
    readonly_fields = ('data',)

@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plano', 'status', 'data_inicio', 'data_fim', 'valor_mensal')
    list_filter = ('plano', 'status', 'data_inicio')
    search_fields = ('usuario__username', 'usuario__email')
    readonly_fields = ('data_inicio',)

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('assinatura', 'valor', 'data', 'status', 'codigo_transacao')
    list_filter = ('status', 'data')
    search_fields = ('assinatura__usuario__username', 'codigo_transacao')
    readonly_fields = ('data',)

@admin.register(DocumentoTreinamento)
class DocumentoTreinamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'status', 'data_upload', 'data_processamento')
    list_filter = ('tipo', 'status', 'data_upload')
    search_fields = ('titulo',)
    readonly_fields = ('data_upload', 'data_processamento')
    ordering = ('-data_upload',)

@admin.register(ModeloIA)
class ModeloIAAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'versao', 'status', 'data_criacao', 'data_ultimo_treinamento')
    list_filter = ('tipo', 'status', 'data_criacao')
    search_fields = ('nome', 'versao')
    readonly_fields = ('data_criacao', 'data_ultimo_treinamento')
    ordering = ('-data_criacao',)

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('chave', 'nivel_acesso', 'ativo', 'total_requisicoes', 'data_criacao', 'data_ultima_requisicao')
    list_filter = ('nivel_acesso', 'ativo', 'data_criacao')
    search_fields = ('chave',)
    readonly_fields = ('data_criacao', 'data_ultima_requisicao', 'total_requisicoes')
    ordering = ('-data_criacao',)

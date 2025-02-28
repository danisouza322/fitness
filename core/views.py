from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import (
    RegistroUsuarioForm, PerfilUsuarioForm, 
    DietaFeedbackForm, AlimentoPersonalizadoForm
)
from .models import (
    PerfilUsuario, Alimento, DietaSugerida, 
    AlimentoPersonalizado
)
from django.db.models import Q
from decimal import Decimal
from .ai_diet import DietaAI

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Por favor, complete seu perfil.')
            return redirect('perfil')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'core/registro.html', {'form': form})

@login_required
def perfil(request):
    try:
        perfil = request.user.perfilusuario
        form = PerfilUsuarioForm(instance=perfil)
    except PerfilUsuario.DoesNotExist:
        perfil = None
        form = PerfilUsuarioForm()
    
    if request.method == 'POST':
        if perfil:
            form = PerfilUsuarioForm(request.POST, instance=perfil)
        else:
            form = PerfilUsuarioForm(request.POST)
            
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('dashboard')
            
    return render(request, 'core/perfil.html', {'form': form})

@login_required
def dashboard(request):
    try:
        perfil = request.user.perfilusuario
        tdee = perfil.calcular_tdee()
        macros = perfil.calcular_macronutrientes()
        
        # Buscar ou criar dieta sugerida
        dieta = gerar_dieta_sugerida(request.user, tdee)
        
        context = {
            'perfil': perfil,
            'tdee': round(tdee),
            'macros': macros,
            'dieta': dieta
        }
        return render(request, 'core/dashboard.html', context)
    except PerfilUsuario.DoesNotExist:
        messages.warning(request, 'Por favor, complete seu perfil primeiro.')
        return redirect('perfil')

def gerar_dieta_sugerida(user, tdee):
    # Converter tdee para Decimal se ainda não for
    tdee = Decimal(str(tdee))
    
    # Criar nova dieta
    dieta = DietaSugerida.objects.create(usuario=user)
    
    # Usar IA para selecionar alimentos
    diet_ai = DietaAI(user)
    
    # Obter distribuição de calorias da configuração
    calorias_cafe = tdee * Decimal(str(diet_ai.config.dist_calorias_cafe))
    calorias_almoco = tdee * Decimal(str(diet_ai.config.dist_calorias_almoco))
    calorias_jantar = tdee * Decimal(str(diet_ai.config.dist_calorias_jantar))
    calorias_lanche = tdee * Decimal(str(diet_ai.config.dist_calorias_lanche))
    
    # Selecionar e ajustar alimentos para cada refeição
    for categoria, calorias in [
        ('C', calorias_cafe),
        ('A', calorias_almoco),
        ('J', calorias_jantar),
        ('L', calorias_lanche)
    ]:
        alimentos = diet_ai.selecionar_alimentos_refeicao(categoria, calorias)
        alimentos_ajustados = diet_ai.ajustar_porcoes(alimentos, calorias)
        
        for item in alimentos_ajustados:
            alimento = item['alimento']
            porcao = item['porcao_ajustada']
            
            # Criar nova instância do alimento com porção ajustada
            novo_alimento = Alimento.objects.create(
                nome=alimento.nome,
                calorias=alimento.calorias,
                proteinas=alimento.proteinas,
                gorduras=alimento.gorduras,
                carboidratos=alimento.carboidratos,
                categoria=alimento.categoria,
                porcao=porcao
            )
            
            # Adicionar à refeição apropriada
            if categoria == 'C':
                dieta.cafe_manha.add(novo_alimento)
            elif categoria == 'A':
                dieta.almoco.add(novo_alimento)
            elif categoria == 'J':
                dieta.jantar.add(novo_alimento)
            else:
                dieta.lanche.add(novo_alimento)
    
    # Registrar log de geração de dieta
    diet_ai.registrar_log(
        'G', 'S',
        f'Dieta gerada com sucesso para {user.username}',
        {
            'tdee': float(tdee),
            'calorias_cafe': float(calorias_cafe),
            'calorias_almoco': float(calorias_almoco),
            'calorias_jantar': float(calorias_jantar),
            'calorias_lanche': float(calorias_lanche)
        }
    )
    
    return dieta

@login_required
def alimentos_personalizados(request):
    alimentos = AlimentoPersonalizado.objects.filter(usuario=request.user).order_by('tipo', 'nome')
    
    if request.method == 'POST':
        form = AlimentoPersonalizadoForm(request.POST)
        if form.is_valid():
            alimento = form.save(commit=False)
            alimento.usuario = request.user
            alimento.save()
            messages.success(request, 'Alimento adicionado com sucesso!')
            return redirect('alimentos_personalizados')
    else:
        form = AlimentoPersonalizadoForm()
    
    return render(request, 'core/alimentos_personalizados.html', {
        'form': form,
        'alimentos': alimentos,
        'alimentos_preferidos': alimentos.filter(tipo='P'),
        'alimentos_restritos': alimentos.filter(tipo='R')
    })

@login_required
def excluir_alimento_personalizado(request, alimento_id):
    alimento = get_object_or_404(AlimentoPersonalizado, id=alimento_id, usuario=request.user)
    nome = alimento.nome
    alimento.delete()
    messages.success(request, f'Alimento "{nome}" removido com sucesso!')
    return redirect('alimentos_personalizados')

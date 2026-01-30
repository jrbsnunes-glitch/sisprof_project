from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import io
from .decorators import (
    permissao_criar_professor,
    permissao_editar_professor,
    permissao_excluir_professor,
    permissao_criar_escola_nucleo,
    permissao_editar_escola_nucleo,
    permissao_excluir_escola_nucleo,
    permissao_criar_escola_dependente,
    permissao_editar_escola_dependente,
    permissao_excluir_escola_dependente,
    permissao_gerar_relatorios,
    permissao_exportar_dados
)

# Models
from .models import (
    Professor, EscolaNucleo, Escola, Cargo, Bairro, Serie, Motivo, 
    PerfilUsuario, LogAuditoria,
    AREA_ATUACAO_CHOICES, SITUACAO_FUNCIONAL_CHOICES, MODALIDADE_CHOICES, 
    TURNO_CHOICES, TIPO_USUARIO_CHOICES
)

# Forms
from .forms import (
    ProfessorForm, EscolaNucleoForm, EscolaForm, CargoForm, BairroForm,
    SerieForm, MotivoForm, LoginForm
)

from .forms_usuarios import (
    UsuarioCreateForm, UsuarioUpdateForm, 
    PerfilUsuarioForm, AlterarSenhaForm
)

# Utils
from .utils.pdf_utils import (
    gerar_pdf_com_cabecalho, 
    obter_estilos_padrao, 
    obter_estilo_tabela_padrao
)

# Importações para PDF
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def login_view(request):
    """View de login"""
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo, {user.username}!")
            return redirect('os_app:index')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = LoginForm()
    return render(request, 'os_app/login.html', {'form': form})


@login_required
def logout_view(request):
    """View de logout"""
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect('os_app:login')


# ============================================================================
# DASHBOARD
# ============================================================================

@login_required
def index(request):
    """Dashboard com estatísticas"""
    # Contadores
    total_professores = Professor.objects.count()
    professores_com_escola = Professor.objects.filter(
        Q(escola_lotacao__isnull=False) | Q(escola_nucleo__isnull=False)
    ).count()
    professores_com_area = Professor.objects.exclude(
        Q(area_atuacao='') | Q(area_atuacao__isnull=True)
    ).count()
    total_escolas = Escola.objects.count()
    total_nucleos = EscolaNucleo.objects.count()
    
    # Últimos professores cadastrados
    ultimos_professores = Professor.objects.select_related(
        'escola_lotacao__nucleo', 'escola_nucleo', 'bairro'
    ).order_by('-data_cadastro')[:5]
    
    # Professores por área de atuação
    professores_por_area = Professor.objects.exclude(
        Q(area_atuacao='') | Q(area_atuacao__isnull=True)
    ).values('area_atuacao').annotate(total=Count('id')).order_by('-total')[:5]
    
    # Top Escolas (dependentes e núcleos) com mais professores
    escolas_com_prof = Escola.objects.annotate(
        total_professores=Count('professores')
    ).filter(total_professores__gt=0).order_by('-total_professores')
    
    nucleos_com_prof = EscolaNucleo.objects.annotate(
        total_professores=Count('professores_nucleo')
    ).filter(total_professores__gt=0).order_by('-total_professores')
    
    # Combinar e pegar top 5
    escolas_top = []
    
    for escola in escolas_com_prof[:5]:
        escolas_top.append({
            'nome': escola.nome,
            'tipo': 'Dependente',
            'nucleo': escola.nucleo.nome if escola.nucleo else '-',
            'total': escola.total_professores,
            'icon': 'building',
            'color': 'success'
        })
    
    for nucleo in nucleos_com_prof[:5]:
        escolas_top.append({
            'nome': nucleo.nome,
            'tipo': 'Núcleo',
            'nucleo': '-',
            'total': nucleo.total_professores,
            'icon': 'buildings',
            'color': 'primary'
        })
    
    escolas_top = sorted(escolas_top, key=lambda x: x['total'], reverse=True)[:5]
    
    context = {
        'total_professores': total_professores,
        'professores_com_escola': professores_com_escola,
        'professores_com_area': professores_com_area,
        'total_escolas': total_escolas,
        'total_nucleos': total_nucleos,
        'ultimos_professores': ultimos_professores,
        'professores_por_area': professores_por_area,
        'escolas_top': escolas_top,
        'area_choices': AREA_ATUACAO_CHOICES,
    }
    
    return render(request, 'os_app/index.html', context)


# ============================================================================
# PROFESSORES - CRUD
# ============================================================================

@login_required
def lista_professores(request):
    """Lista todos os professores com filtros"""
    professores = Professor.objects.select_related(
        'escola_lotacao', 'escola_lotacao__nucleo', 'escola_lotacao__bairro',
        'escola_lotacao__nucleo__bairro', 'escola_nucleo', 'escola_nucleo__bairro',
        'bairro', 'cargo', 'serie', 'motivo_fora_sala'
    )
    
    # Busca
    busca = request.GET.get('busca')
    if busca:
        professores = professores.filter(
            Q(nome__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(matricula__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    # Filtro por núcleo
    nucleo_id = request.GET.get('nucleo')
    if nucleo_id:
        professores = professores.filter(
            Q(escola_lotacao__nucleo_id=nucleo_id) | Q(escola_nucleo_id=nucleo_id)
        )
    
    # Filtro por escola
    escola_lotacao_id = request.GET.get('escola')
    if escola_lotacao_id:
        professores = professores.filter(escola_lotacao_id=escola_lotacao_id)
    
    # Filtro por área
    area = request.GET.get('area')
    if area:
        professores = professores.filter(area_atuacao=area)
    
    professores = professores.order_by('nome')
    
    # Estatísticas
    total_listado = professores.count()
    total_com_escola = professores.filter(
        Q(escola_lotacao__isnull=False) | Q(escola_nucleo__isnull=False)
    ).count()
    total_com_area = professores.exclude(
        Q(area_atuacao='') | Q(area_atuacao__isnull=True)
    ).count()
    total_com_matricula = professores.exclude(
        Q(matricula='') | Q(matricula__isnull=True)
    ).count()
    
    # Para os filtros
    nucleos = EscolaNucleo.objects.all().order_by('nome')
    escolas = Escola.objects.select_related('nucleo').order_by('nucleo__nome', 'nome')
    areas = [a for a in AREA_ATUACAO_CHOICES if a[0]]
    
    context = {
        'professores': professores,
        'nucleos': nucleos,
        'escolas': escolas,
        'areas': areas,
        'area_choices': AREA_ATUACAO_CHOICES,
        'total_listado': total_listado,
        'total_com_escola': total_com_escola,
        'total_com_area': total_com_area,
        'total_com_matricula': total_com_matricula,
    }
    
    return render(request, 'os_app/lista_professores.html', context)


@login_required
@permissao_criar_professor
def novo_professor(request):
    """Cadastra um novo professor"""
    if request.method == 'POST':
        form = ProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            professor = form.save()
            
            # Registra log
            LogAuditoria.registrar(
                usuario=request.user,
                acao='CREATE',
                modelo='Professor',
                objeto_id=professor.id,
                objeto_repr=professor.nome,
                descricao=f'Cadastrou novo professor: {professor.nome}',
                request=request
            )
            
            messages.success(request, 'Professor cadastrado com sucesso!')
            return redirect('os_app:lista_professores')
        else:
            messages.error(request, 'Erro ao cadastrar professor. Verifique os dados.')
    else:
        form = ProfessorForm()
    
    return render(request, 'os_app/novo_professor.html', {'form': form})


@login_required
@permissao_editar_professor
def editar_professor(request, pk):
    """Edita um professor existente"""
    professor = get_object_or_404(Professor, pk=pk)
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST, request.FILES, instance=professor)
        if form.is_valid():
            professor = form.save()
            
            # Registra log
            LogAuditoria.registrar(
                usuario=request.user,
                acao='UPDATE',
                modelo='Professor',
                objeto_id=professor.id,
                objeto_repr=professor.nome,
                descricao=f'Atualizou professor: {professor.nome}',
                request=request
            )
            
            messages.success(request, 'Professor atualizado com sucesso!')
            return redirect('os_app:lista_professores')
        else:
            messages.error(request, 'Erro ao atualizar professor. Verifique os dados.')
    else:
        form = ProfessorForm(instance=professor)
    
    context = {
        'form': form,
        'series': Serie.objects.filter(ativo=True).order_by('nome'),
        'motivos': Motivo.objects.filter(ativo=True).order_by('descricao'),
        'editando': True,
        'professor': professor,
    }
    
    return render(request, 'os_app/novo_professor.html', context)


@login_required
def detalhe_professor(request, pk):
    """Exibe detalhes de um professor"""
    professor = get_object_or_404(Professor, pk=pk)
    return render(request, 'os_app/detalhe_professor.html', {'professor': professor})


@login_required
@permissao_excluir_professor
def deletar_professor(request, pk):
    """Deleta um professor"""
    professor = get_object_or_404(Professor, pk=pk)
    
    if request.method == 'POST':
        nome = professor.nome
        professor_id = professor.id
        professor.delete()
        
        # Registra log
        LogAuditoria.registrar(
            usuario=request.user,
            acao='DELETE',
            modelo='Professor',
            objeto_id=professor_id,
            objeto_repr=nome,
            descricao=f'Excluiu professor: {nome}',
            request=request
        )
        
        messages.success(request, f'Professor {nome} removido com sucesso!')
        return redirect('os_app:lista_professores')
    
    return render(request, 'os_app/confirmar_delete.html', {'professor': professor})


# ============================================================================
# VIEWS AJAX
# ============================================================================

@login_required
def carregar_escolas_por_nucleo(request):
    """Carrega escolas via AJAX baseado no núcleo selecionado"""
    nucleo_id = request.GET.get('nucleo_id')
    
    try:
        nucleo = EscolaNucleo.objects.get(id=nucleo_id)
    except EscolaNucleo.DoesNotExist:
        return JsonResponse([], safe=False)
    
    data = []
    
    # Adicionar o próprio núcleo como primeira opção
    data.append({
        "id": nucleo.id,
        "nome": f"🏫 {nucleo.nome} (Escola Núcleo)",
        "is_nucleo": True
    })
    
    # Adicionar escolas dependentes
    escolas = Escola.objects.filter(nucleo_id=nucleo_id).order_by('nome')
    for e in escolas:
        data.append({
            "id": e.id,
            "nome": f"   └─ {e.nome}",
            "is_nucleo": False
        })
    
    return JsonResponse(data, safe=False)


@login_required
def nova_escola_nucleo_ajax(request):
    """Cadastra escola núcleo via AJAX"""
    if request.method == 'POST':
        form = EscolaNucleoForm(request.POST)
        if form.is_valid():
            nucleo = form.save()
            return JsonResponse({'success': True, 'id': nucleo.id, 'nome': nucleo.nome})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def nova_escola_ajax(request):
    """Cadastra escola de lotação via AJAX"""
    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            escola = form.save()
            nucleo_id = escola.nucleo.id if escola.nucleo else None
            return JsonResponse({
                'success': True, 
                'id': escola.id, 
                'nome': escola.nome,
                'nucleo_id': nucleo_id
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def buscar_bairros_ajax(request):
    """Busca bairros para autocomplete via AJAX"""
    termo = request.GET.get('q', '').strip()
    
    if len(termo) < 2:
        return JsonResponse([], safe=False)
    
    bairros = Bairro.objects.filter(
        Q(nome__icontains=termo) | 
        Q(cidade__icontains=termo) |
        Q(estado__icontains=termo)
    ).values('id', 'nome', 'cidade', 'estado')[:10]
    
    data = [
        {
            'id': b['id'],
            'nome': b['nome'],
            'cidade': b['cidade'] or '',
            'estado': b['estado'] or '',
            'nome_completo': f"{b['nome']}" + (
                f" - {b['cidade']}/{b['estado']}" if b['cidade'] and b['estado'] 
                else f" - {b['cidade']}" if b['cidade'] else ""
            )
        }
        for b in bairros
    ]
    
    return JsonResponse(data, safe=False)


@login_required
def novo_bairro_ajax(request):
    """Cadastra bairro via AJAX"""
    if request.method == 'POST':
        form = BairroForm(request.POST)
        if form.is_valid():
            bairro = form.save()
            nome_completo = str(bairro)
            return JsonResponse({
                'success': True, 
                'id': bairro.id, 
                'nome': bairro.nome,
                'cidade': bairro.cidade or '',
                'estado': bairro.estado or '',
                'nome_completo': nome_completo
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def novo_cargo_ajax(request):
    """Cadastra cargo via AJAX"""
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            cargo = form.save()
            return JsonResponse({
                'success': True,
                'id': cargo.id,
                'nome': cargo.nome
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def nova_serie_ajax(request):
    """Cadastra série via AJAX"""
    if request.method == 'POST':
        form = SerieForm(request.POST)
        if form.is_valid():
            serie = form.save()
            return JsonResponse({
                'success': True,
                'id': serie.id,
                'nome': serie.nome
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def listar_series_ajax(request):
    """Lista todas as séries ativas via AJAX"""
    series = Serie.objects.filter(ativo=True).values('id', 'nome').order_by('nome')
    return JsonResponse(list(series), safe=False)


@login_required
def listar_motivos_ajax(request):
    """Lista todos os motivos ativos via AJAX"""
    motivos = Motivo.objects.filter(ativo=True).values('id', 'descricao').order_by('descricao')
    return JsonResponse(list(motivos), safe=False)


@login_required
def novo_motivo_ajax(request):
    """Cadastra motivo via AJAX"""
    if request.method == 'POST':
        form = MotivoForm(request.POST)
        if form.is_valid():
            motivo = form.save()
            return JsonResponse({
                'success': True,
                'id': motivo.id,
                'descricao': motivo.descricao
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def buscar_professores_ajax(request):
    """Busca professores para substituição via AJAX"""
    termo = request.GET.get('q', '').strip()
    
    if len(termo) < 2:
        return JsonResponse([], safe=False)
    
    professores = Professor.objects.filter(
        Q(nome__icontains=termo) | Q(matricula__icontains=termo)
    ).values('id', 'nome', 'matricula')[:10]
    
    data = [
        {
            'id': p['id'],
            'nome': p['nome'],
            'matricula': p['matricula'] or 'Sem matrícula'
        }
        for p in professores
    ]
    
    return JsonResponse(data, safe=False)


# ============================================================================
# ESCOLAS NÚCLEO
# ============================================================================

@login_required
def lista_escolas_nucleo(request):
    """Lista todas as escolas núcleo"""
    busca = request.GET.get('busca', '').strip()
    
    escolas = EscolaNucleo.objects.all()
    
    if busca:
        escolas = escolas.filter(
            Q(nome__icontains=busca) |
            Q(codigo__icontains=busca) |
            Q(codigo_inep__icontains=busca) |
            Q(cidade__icontains=busca)
        )
    
    escolas = escolas.order_by('nome')
    
    # Adicionar contagem de dependentes
    for escola in escolas:
        escola.num_dependentes = Escola.objects.filter(nucleo=escola).count()
        escola.num_professores = Professor.objects.filter(escola_nucleo=escola).count()
    
    # Paginação
    paginator = Paginator(escolas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'escolas': page_obj,
        'busca': busca,
        'total': escolas.count()
    }
    return render(request, 'os_app/lista_escolas_nucleo.html', context)


@login_required
@permissao_criar_escola_nucleo
def nova_escola_nucleo(request):
    """Cadastra nova escola núcleo"""
    if request.method == 'POST':
        form = EscolaNucleoForm(request.POST)
        if form.is_valid():
            escola = form.save()
            messages.success(request, f'Escola Núcleo "{escola.nome}" cadastrada com sucesso!')
            return redirect('os_app:lista_escolas_nucleo')
        else:
            messages.error(request, 'Erro ao cadastrar escola núcleo. Verifique os dados.')
    else:
        form = EscolaNucleoForm()
    
    return render(request, 'os_app/form_escola_nucleo.html', {
        'form': form, 
        'titulo': 'Cadastrar Escola Núcleo'
    })


@login_required
@permissao_editar_escola_nucleo
def editar_escola_nucleo(request, pk):
    """Edita escola núcleo existente"""
    escola = get_object_or_404(EscolaNucleo, pk=pk)
    
    if request.method == 'POST':
        form = EscolaNucleoForm(request.POST, instance=escola)
        if form.is_valid():
            escola = form.save()
            messages.success(request, f'Escola Núcleo "{escola.nome}" atualizada com sucesso!')
            return redirect('os_app:lista_escolas_nucleo')
        else:
            messages.error(request, 'Erro ao atualizar escola núcleo. Verifique os dados.')
    else:
        form = EscolaNucleoForm(instance=escola)
    
    context = {
        'form': form,
        'titulo': f'Editar Escola Núcleo: {escola.nome}',
        'escola': escola,
        'editando': True
    }
    return render(request, 'os_app/form_escola_nucleo.html', context)


@login_required
@permissao_excluir_escola_nucleo
def deletar_escola_nucleo(request, pk):
    """Deleta escola núcleo"""
    escola = get_object_or_404(EscolaNucleo, pk=pk)
    
    num_dependentes = Escola.objects.filter(nucleo=escola).count()
    num_professores = Professor.objects.filter(escola_nucleo=escola).count()
    
    if request.method == 'POST':
        if num_dependentes > 0 or num_professores > 0:
            messages.error(
                request, 
                f'Não é possível excluir "{escola.nome}" pois há '
                f'{num_dependentes} escola(s) dependente(s) e '
                f'{num_professores} professor(es) vinculado(s).'
            )
            return redirect('os_app:lista_escolas_nucleo')
        
        nome = escola.nome
        escola.delete()
        messages.success(request, f'Escola Núcleo "{nome}" removida com sucesso!')
        return redirect('os_app:lista_escolas_nucleo')
    
    context = {
        'escola': escola,
        'num_dependentes': num_dependentes,
        'num_professores': num_professores,
        'pode_deletar': num_dependentes == 0 and num_professores == 0
    }
    return render(request, 'os_app/confirmar_delete_escola_nucleo.html', context)


# ============================================================================
# ESCOLAS DEPENDENTES
# ============================================================================

@login_required
def lista_escolas_dependentes(request):
    """Lista todas as escolas dependentes"""
    busca = request.GET.get('busca', '').strip()
    nucleo_id = request.GET.get('nucleo', '')
    
    escolas = Escola.objects.select_related('nucleo').all()
    
    if busca:
        escolas = escolas.filter(
            Q(nome__icontains=busca) |
            Q(codigo_inep__icontains=busca) |
            Q(cidade__icontains=busca) |
            Q(nucleo__nome__icontains=busca)
        )
    
    if nucleo_id:
        escolas = escolas.filter(nucleo_id=nucleo_id)
    
    escolas = escolas.order_by('nucleo__nome', 'nome')
    
    # Adicionar contagem de professores
    for escola in escolas:
        escola.num_professores = Professor.objects.filter(escola_lotacao=escola).count()
    
    # Paginação
    paginator = Paginator(escolas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lista de núcleos para o filtro
    nucleos = EscolaNucleo.objects.all().order_by('nome')
    
    context = {
        'escolas': page_obj,
        'nucleos': nucleos,
        'busca': busca,
        'nucleo_selecionado': nucleo_id,
        'total': escolas.count()
    }
    return render(request, 'os_app/lista_escolas_dependentes.html', context)


@login_required
@permissao_criar_escola_dependente
def nova_escola_dependente(request):
    """Cadastra nova escola dependente"""
    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            escola = form.save()
            messages.success(request, f'Escola Dependente "{escola.nome}" cadastrada com sucesso!')
            return redirect('os_app:lista_escolas_dependentes')
        else:
            messages.error(request, 'Erro ao cadastrar escola dependente. Verifique os dados.')
    else:
        form = EscolaForm()
    
    return render(request, 'os_app/form_escola_dependente.html', {
        'form': form, 
        'titulo': 'Cadastrar Escola Dependente'
    })


@login_required
@permissao_editar_escola_dependente
def editar_escola_dependente(request, pk):
    """Edita escola dependente existente"""
    escola = get_object_or_404(Escola, pk=pk)
    
    if request.method == 'POST':
        form = EscolaForm(request.POST, instance=escola)
        if form.is_valid():
            escola = form.save()
            messages.success(request, f'Escola Dependente "{escola.nome}" atualizada com sucesso!')
            return redirect('os_app:lista_escolas_dependentes')
        else:
            messages.error(request, 'Erro ao atualizar escola dependente. Verifique os dados.')
    else:
        form = EscolaForm(instance=escola)
    
    context = {
        'form': form,
        'titulo': f'Editar Escola Dependente: {escola.nome}',
        'escola': escola,
        'editando': True
    }
    return render(request, 'os_app/form_escola_dependente.html', context)


@login_required
@permissao_excluir_escola_dependente
def deletar_escola_dependente(request, pk):
    """Deleta escola dependente"""
    escola = get_object_or_404(Escola, pk=pk)
    
    num_professores = Professor.objects.filter(escola_lotacao=escola).count()
    
    if request.method == 'POST':
        if num_professores > 0:
            messages.error(
                request, 
                f'Não é possível excluir "{escola.nome}" pois há '
                f'{num_professores} professor(es) vinculado(s).'
            )
            return redirect('os_app:lista_escolas_dependentes')
        
        nome = escola.nome
        escola.delete()
        messages.success(request, f'Escola Dependente "{nome}" removida com sucesso!')
        return redirect('os_app:lista_escolas_dependentes')
    
    context = {
        'escola': escola,
        'num_professores': num_professores,
        'pode_deletar': num_professores == 0
    }
    return render(request, 'os_app/confirmar_delete_escola_dependente.html', context)


@login_required
@permissao_gerar_relatorios
def relatorios_filtros(request):
    """Tela de filtros e seleção de campos para relatórios personalizados"""
    
    # Dados para os filtros
    nucleos = EscolaNucleo.objects.all().order_by('nome')
    escolas = Escola.objects.select_related('nucleo').order_by('nucleo__nome', 'nome')
    areas = [a for a in AREA_ATUACAO_CHOICES if a[0]]
    situacoes = [s for s in SITUACAO_FUNCIONAL_CHOICES if s[0]]
    modalidades = [m for m in MODALIDADE_CHOICES if m[0]]
    turnos = [t for t in TURNO_CHOICES if t[0]]
    cargos = Cargo.objects.filter(ativo=True).order_by('nome')
    series = Serie.objects.all().order_by('nome')
    bairros = Bairro.objects.all().order_by('nome')

    from .models import MATERIAS_CHOICES
    materias = [m for m in MATERIAS_CHOICES if m[0]]
    
    # Campos disponíveis para seleção
    campos_disponiveis = [
        {'id': 'id', 'nome': 'ID', 'grupo': 'Básico'},
        {'id': 'nome', 'nome': 'Nome', 'grupo': 'Básico'},
        {'id': 'cpf', 'nome': 'CPF', 'grupo': 'Básico'},
        {'id': 'email', 'nome': 'Email', 'grupo': 'Básico'},
        {'id': 'telefone', 'nome': 'Telefone', 'grupo': 'Contato'},
        {'id': 'celular', 'nome': 'Celular', 'grupo': 'Contato'},
        {'id': 'cargo', 'nome': 'Cargo', 'grupo': 'Profissional'},
        {'id': 'situacao_funcional', 'nome': 'Situação Funcional', 'grupo': 'Profissional'},
        {'id': 'matricula', 'nome': 'Matrícula', 'grupo': 'Profissional'},
        {'id': 'ref_global', 'nome': 'Ref. Global', 'grupo': 'Profissional'},
        {'id': 'area_atuacao', 'nome': 'Área de Atuação', 'grupo': 'Profissional'},
        {'id': 'materias', 'nome': 'Matérias', 'grupo': 'Profissional'},  # ← ADICIONAR ESTA LINHA
        {'id': 'modalidade', 'nome': 'Modalidade', 'grupo': 'Profissional'},
        {'id': 'turno', 'nome': 'Turno', 'grupo': 'Profissional'},
        {'id': 'serie', 'nome': 'Série', 'grupo': 'Profissional'},
        {'id': 'em_sala', 'nome': 'Em Sala', 'grupo': 'Profissional'},
        {'id': 'escola_lotacao', 'nome': 'Escola', 'grupo': 'Lotação'},
        {'id': 'escola_nucleo', 'nome': 'Núcleo', 'grupo': 'Lotação'},
        {'id': 'endereco_escola', 'nome': 'Endereço Escola', 'grupo': 'Lotação'},
        {'id': 'zona_escola', 'nome': 'Zona Escola', 'grupo': 'Lotação'},
        {'id': 'endereco', 'nome': 'Endereço Residencial', 'grupo': 'Endereço'},
        {'id': 'bairro', 'nome': 'Bairro', 'grupo': 'Endereço'},
        {'id': 'cidade', 'nome': 'Cidade', 'grupo': 'Endereço'},
        {'id': 'estado', 'nome': 'Estado', 'grupo': 'Endereço'},
        {'id': 'cep', 'nome': 'CEP', 'grupo': 'Endereço'},
        {'id': 'data_nascimento', 'nome': 'Data Nascimento', 'grupo': 'Dados Pessoais'},
        {'id': 'sexo', 'nome': 'Sexo', 'grupo': 'Dados Pessoais'},
        {'id': 'data_cadastro', 'nome': 'Data Cadastro', 'grupo': 'Sistema'},
    ]
    
    # Agrupa campos por categoria
    campos_por_grupo = {}
    for campo in campos_disponiveis:
        grupo = campo['grupo']
        if grupo not in campos_por_grupo:
            campos_por_grupo[grupo] = []
        campos_por_grupo[grupo].append(campo)
    
    context = {
        'nucleos': nucleos,
        'escolas': escolas,
        'areas': areas,
        'situacoes': situacoes,
        'modalidades': modalidades,
        'turnos': turnos,
        'cargos': cargos,
        'series': series,
        'bairros': bairros,
        'campos_disponiveis': campos_disponiveis,
        'campos_por_grupo': campos_por_grupo,
        'pdf_available': PDF_AVAILABLE,
        'materias': materias,
    }
    
    return render(request, 'os_app/relatorios_filtros.html', context)


@login_required
@permissao_gerar_relatorios
def relatorios_resultado(request):
    """Gera e exibe o relatório baseado nos filtros e campos selecionados - COM FILTROS DE INTERVALO"""
    
    # Captura os filtros - INCLUINDO INTERVALOS
    professor_id = request.GET.get('professor_id')
    professor_id_inicio = request.GET.get('professor_id_inicio')
    professor_id_fim = request.GET.get('professor_id_fim')
    ref_global = request.GET.get('ref_global')
    nucleo_id = request.GET.get('nucleo')
    escola_id = request.GET.get('escola')
    area = request.GET.get('area')
    materia = request.GET.get('materia')
    situacao = request.GET.get('situacao')
    em_sala = request.GET.get('em_sala')
    cidade = request.GET.get('cidade')
    cargo_id = request.GET.get('cargo')
    serie_id = request.GET.get('serie')
    serie_id_inicio = request.GET.get('serie_id_inicio')
    serie_id_fim = request.GET.get('serie_id_fim')
    modalidade = request.GET.get('modalidade')
    turno = request.GET.get('turno')
    turno_inicio = request.GET.get('turno_inicio')
    turno_fim = request.GET.get('turno_fim')
    bairro_id = request.GET.get('bairro')
    
    # Captura campos selecionados
    campos_selecionados = request.GET.getlist('campos')
    if not campos_selecionados:
        # Campos padrão se nenhum selecionado
        campos_selecionados = ['id', 'nome', 'cargo', 'situacao_funcional', 'escola_lotacao', 'area_atuacao']
    
    # Monta a query com select_related
    professores = Professor.objects.select_related(
        'escola_lotacao',
        'escola_lotacao__nucleo',
        'escola_lotacao__bairro',
        'escola_nucleo',
        'escola_nucleo__bairro',
        'bairro',
        'cargo',
        'serie'
    ).all()
    
    # Aplica filtros
    filtros_aplicados = []
    
    # FILTRO DE ID - INTERVALO OU ÚNICO
    if professor_id_inicio and professor_id_fim:
        professores = professores.filter(id__gte=professor_id_inicio, id__lte=professor_id_fim)
        filtros_aplicados.append(f"ID: de {professor_id_inicio} até {professor_id_fim}")
    elif professor_id_inicio:
        professores = professores.filter(id__gte=professor_id_inicio)
        filtros_aplicados.append(f"ID: a partir de {professor_id_inicio}")
    elif professor_id_fim:
        professores = professores.filter(id__lte=professor_id_fim)
        filtros_aplicados.append(f"ID: até {professor_id_fim}")
    elif professor_id:
        professores = professores.filter(id=professor_id)
        filtros_aplicados.append(f"ID: {professor_id}")
    
    if ref_global:
        professores = professores.filter(ref_global__icontains=ref_global)
        filtros_aplicados.append(f"Ref. Global: {ref_global}")
    
    if nucleo_id:
        professores = professores.filter(
            Q(escola_lotacao__nucleo_id=nucleo_id) | 
            Q(escola_nucleo_id=nucleo_id)
        )
        try:
            nucleo = EscolaNucleo.objects.get(id=nucleo_id)
            filtros_aplicados.append(f"Núcleo: {nucleo.nome}")
        except:
            pass
    
    if escola_id:
        professores = professores.filter(escola_lotacao_id=escola_id)
        try:
            escola = Escola.objects.get(id=escola_id)
            filtros_aplicados.append(f"Escola: {escola.nome}")
        except:
            pass
    
    if area:
        professores = professores.filter(area_atuacao=area)
        area_nome = dict(AREA_ATUACAO_CHOICES).get(area, area)
        filtros_aplicados.append(f"Área: {area_nome}")
    
    if situacao:
        professores = professores.filter(situacao_funcional=situacao)
        sit_nome = dict(SITUACAO_FUNCIONAL_CHOICES).get(situacao, situacao)
        filtros_aplicados.append(f"Situação: {sit_nome}")
    
    if em_sala:
        if em_sala == 'sim':
            professores = professores.filter(em_sala=True)
            filtros_aplicados.append("Em Sala: Sim")
        elif em_sala == 'nao':
            professores = professores.filter(em_sala=False)
            filtros_aplicados.append("Em Sala: Não")
    
    if cidade:
        professores = professores.filter(cidade__icontains=cidade)
        filtros_aplicados.append(f"Cidade: {cidade}")
    
    if cargo_id:
        professores = professores.filter(cargo_id=cargo_id)
        try:
            cargo = Cargo.objects.get(id=cargo_id)
            filtros_aplicados.append(f"Cargo: {cargo.nome}")
        except:
            pass
    
    # FILTRO DE SÉRIE - INTERVALO OU ÚNICO
    if serie_id_inicio and serie_id_fim:
        professores = professores.filter(serie_id__gte=serie_id_inicio, serie_id__lte=serie_id_fim)
        try:
            serie_ini = Serie.objects.get(id=serie_id_inicio)
            serie_fim = Serie.objects.get(id=serie_id_fim)
            filtros_aplicados.append(f"Série: de {serie_ini.nome} até {serie_fim.nome}")
        except:
            filtros_aplicados.append(f"Série: de ID {serie_id_inicio} até {serie_id_fim}")
    elif serie_id_inicio:
        professores = professores.filter(serie_id__gte=serie_id_inicio)
        try:
            serie_ini = Serie.objects.get(id=serie_id_inicio)
            filtros_aplicados.append(f"Série: a partir de {serie_ini.nome}")
        except:
            filtros_aplicados.append(f"Série: a partir de ID {serie_id_inicio}")
    elif serie_id_fim:
        professores = professores.filter(serie_id__lte=serie_id_fim)
        try:
            serie_fim = Serie.objects.get(id=serie_id_fim)
            filtros_aplicados.append(f"Série: até {serie_fim.nome}")
        except:
            filtros_aplicados.append(f"Série: até ID {serie_id_fim}")
    elif serie_id:
        professores = professores.filter(serie_id=serie_id)
        try:
            serie = Serie.objects.get(id=serie_id)
            filtros_aplicados.append(f"Série: {serie.nome}")
        except:
            pass
    
    if modalidade:
        professores = professores.filter(modalidade=modalidade)
        mod_nome = dict(MODALIDADE_CHOICES).get(modalidade, modalidade)
        filtros_aplicados.append(f"Modalidade: {mod_nome}")
    
    # FILTRO DE TURNO - INTERVALO OU LISTA
    if turno_inicio and turno_fim:
        # Busca turnos entre início e fim na ordem das choices
        turnos_choices = [t[0] for t in TURNO_CHOICES if t[0]]
        try:
            idx_inicio = turnos_choices.index(turno_inicio)
            idx_fim = turnos_choices.index(turno_fim)
            turnos_no_intervalo = turnos_choices[idx_inicio:idx_fim+1]
            professores = professores.filter(turno__in=turnos_no_intervalo)
            turno_ini_nome = dict(TURNO_CHOICES).get(turno_inicio, turno_inicio)
            turno_fim_nome = dict(TURNO_CHOICES).get(turno_fim, turno_fim)
            filtros_aplicados.append(f"Turno: de {turno_ini_nome} até {turno_fim_nome}")
        except:
            filtros_aplicados.append(f"Turno: intervalo inválido")
    elif turno_inicio:
        turnos_choices = [t[0] for t in TURNO_CHOICES if t[0]]
        try:
            idx_inicio = turnos_choices.index(turno_inicio)
            turnos_a_partir = turnos_choices[idx_inicio:]
            professores = professores.filter(turno__in=turnos_a_partir)
            turno_ini_nome = dict(TURNO_CHOICES).get(turno_inicio, turno_inicio)
            filtros_aplicados.append(f"Turno: a partir de {turno_ini_nome}")
        except:
            pass
    elif turno_fim:
        turnos_choices = [t[0] for t in TURNO_CHOICES if t[0]]
        try:
            idx_fim = turnos_choices.index(turno_fim)
            turnos_ate = turnos_choices[:idx_fim+1]
            professores = professores.filter(turno__in=turnos_ate)
            turno_fim_nome = dict(TURNO_CHOICES).get(turno_fim, turno_fim)
            filtros_aplicados.append(f"Turno: até {turno_fim_nome}")
        except:
            pass
    elif turno:
        professores = professores.filter(turno=turno)
        turno_nome = dict(TURNO_CHOICES).get(turno, turno)
        filtros_aplicados.append(f"Turno: {turno_nome}")
    
    if bairro_id:
        professores = professores.filter(bairro_id=bairro_id)
        try:
            bairro = Bairro.objects.get(id=bairro_id)
            filtros_aplicados.append(f"Bairro: {bairro.nome}")
        except:
            pass

    if materia:
        from .models import MATERIAS_CHOICES
        professores = professores.filter(materias__icontains=materia)
        materia_nome = dict(MATERIAS_CHOICES).get(materia, materia)
        filtros_aplicados.append(f"Matéria: {materia_nome}")
    
    # Ordena
    professores = professores.order_by('nome')
    
    # Estatísticas
    total = professores.count()
    com_escola = professores.filter(
        Q(escola_lotacao__isnull=False) | Q(escola_nucleo__isnull=False)
    ).count()
    sem_escola = total - com_escola
    
    # Mapeamento de campos para labels
    campos_labels = {
        'id': 'ID',
        'nome': 'Nome',
        'cpf': 'CPF',
        'email': 'Email',
        'telefone': 'Telefone',
        'celular': 'Celular',
        'cargo': 'Cargo',
        'situacao_funcional': 'Situação',
        'matricula': 'Matrícula',
        'ref_global': 'Ref. Global',
        'area_atuacao': 'Área',
        'materias': 'Matérias',
        'modalidade': 'Modalidade',
        'turno': 'Turno',
        'serie': 'Série',
        'em_sala': 'Em Sala',
        'escola': 'Escola',
        'escola_nucleo': 'Núcleo',
        'endereco_escola': 'End. Escola',
        'zona_escola': 'Zona',
        'endereco': 'Endereço',
        'bairro': 'Bairro',
        'cidade': 'Cidade',
        'estado': 'Estado',
        'cep': 'CEP',
        'data_nascimento': 'Dt. Nasc.',
        'sexo': 'Sexo',
        'data_cadastro': 'Dt. Cadastro',
    }
    
    from django.conf import settings
    context = {
        'professores': professores,
        'filtros_aplicados': filtros_aplicados,
        'total': total,
        'com_escola': com_escola,
        'sem_escola': sem_escola,
        'campos_selecionados': campos_selecionados,
        'campos_labels': campos_labels,
        'media_url': getattr(settings, 'MEDIA_URL', '/media/'),
    }
    
    return render(request, 'os_app/relatorios_resultado.html', context)


@login_required
@permissao_exportar_dados
def relatorios_pdf(request):
    """Gera PDF do relatório com cabeçalho padronizado"""
    
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import Paragraph, Spacer, Table
        from datetime import datetime
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
    
    if not PDF_AVAILABLE:
        return HttpResponse("ReportLab não está instalado. Execute: pip install reportlab", status=500)
    
    # Captura campos selecionados e filtros
    campos_selecionados = request.GET.getlist('campos')
    if not campos_selecionados:
        campos_selecionados = ['id', 'nome', 'cargo', 'situacao_funcional', 'escola']
    
    # Mapeamento de labels
    campos_labels_pdf = {
        'id': 'ID',
        'nome': 'Nome',
        'cpf': 'CPF',
        'email': 'E-mail',
        'telefone': 'Telefone',
        'celular': 'Celular',
        'cargo': 'Cargo',
        'situacao_funcional': 'Situação',
        'matricula': 'Matrícula',
        'ref_global': 'Ref. Global',
        'area_atuacao': 'Área de Atuação',
        'modalidade': 'Modalidade',
        'turno': 'Turno',
        'serie': 'Série',
        'em_sala': 'Em Sala',
        'escola': 'Escola',
        'escola_nucleo': 'Núcleo',
        'endereco_escola': 'Endereço Escola',
        'zona_escola': 'Zona',
        'endereco': 'Endereço',
        'bairro': 'Bairro',
        'cidade': 'Cidade',
        'estado': 'Estado',
        'cep': 'CEP',
        'data_nascimento': 'Dt. Nasc.',
        'sexo': 'Sexo',
        'data_cadastro': 'Dt. Cadastro',
    }
    
    # Monta query com filtros
    professores = Professor.objects.select_related(
        'escola_lotacao', 'escola_lotacao__nucleo', 'escola_lotacao__bairro',
        'escola_nucleo', 'escola_nucleo__bairro',
        'bairro', 'cargo', 'serie'
    ).all()
    
    # Aplica filtros (MANTENHA SEU CÓDIGO DE FILTROS EXISTENTE)
    professor_id = request.GET.get('professor_id')
    ref_global = request.GET.get('ref_global')
    nucleo_id = request.GET.get('nucleo')
    escola_id = request.GET.get('escola')
    area = request.GET.get('area')
    situacao = request.GET.get('situacao')
    em_sala = request.GET.get('em_sala')
    cidade = request.GET.get('cidade')
    cargo_id = request.GET.get('cargo')
    serie_id = request.GET.get('serie')
    modalidade = request.GET.get('modalidade')
    turno = request.GET.get('turno')
    bairro_id = request.GET.get('bairro')
    
    if professor_id:
        professores = professores.filter(id=professor_id)
    if ref_global:
        professores = professores.filter(ref_global__icontains=ref_global)
    if nucleo_id:
        professores = professores.filter(Q(escola_lotacao__nucleo_id=nucleo_id) | Q(escola_nucleo_id=nucleo_id))
    if escola_id:
        professores = professores.filter(escola_lotacao_id=escola_id)
    if area:
        professores = professores.filter(area_atuacao=area)
    if situacao:
        professores = professores.filter(situacao_funcional=situacao)
    if em_sala:
        if em_sala == 'sim':
            professores = professores.filter(em_sala=True)
        elif em_sala == 'nao':
            professores = professores.filter(em_sala=False)
    if cidade:
        professores = professores.filter(cidade__icontains=cidade)
    if cargo_id:
        professores = professores.filter(cargo_id=cargo_id)
    if serie_id:
        professores = professores.filter(serie_id=serie_id)
    if modalidade:
        professores = professores.filter(modalidade=modalidade)
    if turno:
        professores = professores.filter(turno=turno)
    if bairro_id:
        professores = professores.filter(bairro_id=bairro_id)
    
    professores = professores.order_by('nome')
    
    # ============================================================
    # NOVA IMPLEMENTAÇÃO COM CABEÇALHO PADRONIZADO
    # ============================================================
    
    elements = []
    styles = obter_estilos_padrao()
    
    # Informações do relatório
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    info_text = f"<para align=center><font size=9 color='#666666'>Total: {professores.count()} professores</font></para>"
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 0.7*inch))
    
    # Monta tabela
    data = []
    
    # Cabeçalhos
    header = []
    for campo in campos_selecionados:
        label = campos_labels_pdf.get(campo, campo.upper())
        header.append(Paragraph(f"<b>{label}</b>", styles['Normal']))
    data.append(header)
    
    # Dados
    for prof in professores:
        row = []
        for campo in campos_selecionados:
            valor = get_campo_valor_pdf(prof, campo)  # MANTENHA SUA FUNÇÃO
            # Limita tamanho do texto
            if len(str(valor)) > 35:
                valor = str(valor)[:32] + '...'
            row.append(Paragraph(str(valor), styles['Normal']))
        data.append(row)
    
    # Calcula larguras
    larguras = []
    for campo in campos_selecionados:
        if campo == 'id':
            larguras.append(0.4 * inch)
        elif campo == 'nome':
            larguras.append(1.5 * inch)
        elif campo == 'cpf':
            larguras.append(1.0 * inch)
        elif campo == 'ref_global':
            larguras.append(0.8 * inch)
        elif campo in ['telefone', 'celular']:
            larguras.append(0.9 * inch)
        elif campo in ['em_sala', 'sexo', 'estado']:
            larguras.append(0.5 * inch)
        else:
            larguras.append(1.2 * inch)
    
    # Ajusta larguras
    largura_disponivel = 10.5 * inch
    total_largura = sum(larguras)
    if total_largura > largura_disponivel:
        fator = largura_disponivel / total_largura
        larguras = [l * fator for l in larguras]
    
    # Cria tabela com estilo padronizado
    table = Table(data, colWidths=larguras)
    table.setStyle(obter_estilo_tabela_padrao())
    
    elements.append(table)
    
    # ============================================================
    # GERA PDF COM CABEÇALHO PADRONIZADO
    # ============================================================
    buffer = gerar_pdf_com_cabecalho(
        titulo_relatorio="Relatório de Professores",
        conteudo=elements,
        orientacao='paisagem'
    )
    
    # Prepara resposta: inline = exibir PDF na tela (preview); attachment = download
    response = HttpResponse(content_type='application/pdf')
    filename = f'relatorio_professores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    response.write(buffer.getvalue())
    
    return response


def get_campo_valor_pdf(professor, campo):
    """Retorna o valor formatado de um campo do professor para PDF"""
    
    if campo == 'id':
        return str(professor.id)
    elif campo == 'nome':
        return professor.nome
    elif campo == 'cpf':
        if hasattr(professor, 'cpf_formatado') and callable(professor.cpf_formatado):
            return professor.cpf_formatado()
        return professor.cpf if professor.cpf else '-'
    elif campo == 'email':
        return professor.email if professor.email else '-'
    elif campo == 'telefone':
        return professor.telefone if professor.telefone else '-'
    elif campo == 'celular':
        return professor.celular if professor.celular else '-'
    elif campo == 'cargo':
        return professor.cargo.nome if professor.cargo else '-'
    elif campo == 'situacao_funcional':
        return professor.get_situacao_funcional_display() if professor.situacao_funcional else '-'
    elif campo == 'matricula':
        return professor.matricula if professor.matricula else '-'
    elif campo == 'ref_global':
        return professor.ref_global if professor.ref_global else '-'
    elif campo == 'area_atuacao':
        return professor.get_area_atuacao_display() if professor.area_atuacao else '-'
    elif campo == 'materias':
        if professor.materias:
            materias_list = professor.get_materias_display()
            if materias_list:
                materias_str = ', '.join(materias_list)
                if len(materias_str) > 50:
                    return materias_str[:47] + '...'
                return materias_str
        return '-'
    
    elif campo == 'modalidade':
        return professor.get_modalidade_display() if professor.modalidade else '-'
    elif campo == 'modalidade':
        return professor.get_modalidade_display() if professor.modalidade else '-'
    elif campo == 'turno':
        return professor.get_turno_display() if professor.turno else '-'
    elif campo == 'serie':
        return professor.serie.nome if professor.serie else '-'
    elif campo == 'em_sala':
        return 'Sim' if professor.em_sala else 'Não'
    elif campo == 'escola':
        if professor.escola:
            return professor.escola.nome
        elif professor.escola_nucleo:
            return professor.escola_nucleo.nome + ' (Núcleo)'
        return '-'
    elif campo == 'escola_nucleo':
        if professor.escola_nucleo:
            return professor.escola_nucleo.nome
        elif professor.escola and professor.escola.nucleo:
            return professor.escola.nucleo.nome
        return '-'
    elif campo == 'endereco_escola':
        if professor.escola:
            end = professor.escola.endereco or ''
            num = professor.escola.numero or ''
            return f"{end}, {num}" if end and num else end or num or '-'
        elif professor.escola_nucleo:
            end = professor.escola_nucleo.endereco or ''
            num = professor.escola_nucleo.numero or ''
            return f"{end}, {num}" if end and num else end or num or '-'
        return '-'
    elif campo == 'zona_escola':
        if professor.escola:
            return professor.escola.get_zona_display()
        elif professor.escola_nucleo:
            return professor.escola_nucleo.get_zona_display()
        return '-'
    elif campo == 'endereco':
        return professor.endereco if professor.endereco else '-'
    elif campo == 'bairro':
        return professor.bairro.nome if professor.bairro else '-'
    elif campo == 'cidade':
        return professor.cidade if professor.cidade else '-'
    elif campo == 'estado':
        return professor.estado if professor.estado else '-'
    elif campo == 'cep':
        return professor.cep if professor.cep else '-'
    elif campo == 'data_nascimento':
        return professor.data_nascimento.strftime("%d/%m/%Y") if professor.data_nascimento else '-'
    elif campo == 'sexo':
        return professor.get_sexo_display() if hasattr(professor, 'sexo') and professor.sexo else '-'
    elif campo == 'data_cadastro':
        return professor.data_cadastro.strftime("%d/%m/%Y") if professor.data_cadastro else '-'
    else:
        # Tenta pegar o atributo genérico
        valor = getattr(professor, campo, '-')
        return str(valor) if valor else '-'
    

    # ============================================================================
# VIEWS DE LOG DE AUDITORIA
# Arquivo: os_app/views.py (ADICIONAR)
# ============================================================================

from .models import LogAuditoria
from django.db.models import Count, Q
from datetime import datetime, timedelta

@login_required
def logs_auditoria(request):
    """Visualizar logs de auditoria"""
    # Apenas administradores podem ver logs
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('os_app:index')
    
    # Filtros
    logs = LogAuditoria.objects.select_related('usuario').all()
    
    # Filtro por usuário
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    
    # Filtro por ação
    acao = request.GET.get('acao')
    if acao:
        logs = logs.filter(acao=acao)
    
    # Filtro por modelo
    modelo = request.GET.get('modelo')
    if modelo:
        logs = logs.filter(modelo=modelo)
    
    # Filtro por período
    periodo = request.GET.get('periodo')
    if periodo:
        hoje = datetime.now().date()
        if periodo == 'hoje':
            logs = logs.filter(data_hora__date=hoje)
        elif periodo == 'semana':
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            logs = logs.filter(data_hora__date__gte=inicio_semana)
        elif periodo == 'mes':
            logs = logs.filter(
                data_hora__year=hoje.year,
                data_hora__month=hoje.month
            )
    
    # Filtro por data específica
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if data_inicio:
        logs = logs.filter(data_hora__date__gte=data_inicio)
    if data_fim:
        logs = logs.filter(data_hora__date__lte=data_fim)
    
    # Busca por texto
    busca = request.GET.get('busca')
    if busca:
        logs = logs.filter(
            Q(descricao__icontains=busca) |
            Q(objeto_repr__icontains=busca) |
            Q(usuario__username__icontains=busca)
        )
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)  # 50 logs por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_logs = logs.count()
    logs_hoje = LogAuditoria.objects.filter(data_hora__date=datetime.now().date()).count()
    
    # Ações mais comuns (últimos 7 dias)
    sete_dias_atras = datetime.now() - timedelta(days=7)
    acoes_comuns = LogAuditoria.objects.filter(
        data_hora__gte=sete_dias_atras
    ).values('acao').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Usuários mais ativos (últimos 7 dias)
    usuarios_ativos = LogAuditoria.objects.filter(
        data_hora__gte=sete_dias_atras,
        usuario__isnull=False
    ).values(
        'usuario__username'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Lista de usuários para filtro
    from django.contrib.auth.models import User
    usuarios = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'page_obj': page_obj,
        'total_logs': total_logs,
        'logs_hoje': logs_hoje,
        'acoes_comuns': acoes_comuns,
        'usuarios_ativos': usuarios_ativos,
        'usuarios': usuarios,
        'acao_choices': LogAuditoria.ACAO_CHOICES,
        'modelo_choices': LogAuditoria.MODELO_CHOICES,
    }
    
    return render(request, 'os_app/logs_auditoria.html', context)


@login_required
def log_detalhe(request, log_id):
    """Detalhe de um log específico"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('os_app:index')
    
    log = get_object_or_404(LogAuditoria, id=log_id)
    
    context = {
        'log': log,
    }
    
    return render(request, 'os_app/log_detalhe.html', context)


@login_required
def logs_meu_historico(request):
    """Histórico de ações do usuário logado"""
    # Logs do usuário atual
    logs = LogAuditoria.objects.filter(
        usuario=request.user
    ).order_by('-data_hora')[:100]  # Últimos 100
    
    # Estatísticas do usuário
    total_acoes = logs.count()
    ultima_acao = logs.first()
    
    # Ações por tipo
    acoes_por_tipo = LogAuditoria.objects.filter(
        usuario=request.user
    ).values('acao').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'logs': logs,
        'total_acoes': total_acoes,
        'ultima_acao': ultima_acao,
        'acoes_por_tipo': acoes_por_tipo,
    }
    
    return render(request, 'os_app/meu_historico.html', context)


@login_required
def logs_exportar(request):
    """Exportar logs para CSV"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('os_app:index')
    
    import csv
    from django.http import HttpResponse
    
    # Aplica mesmos filtros da view principal
    logs = LogAuditoria.objects.select_related('usuario').all()
    
    # Aplica filtros (copiar lógica da view logs_auditoria)
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    
    acao = request.GET.get('acao')
    if acao:
        logs = logs.filter(acao=acao)
    
    # ... outros filtros ...
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="logs_auditoria_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Adiciona BOM para Excel reconhecer UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'ID',
        'Data/Hora',
        'Usuário',
        'Ação',
        'Modelo',
        'Objeto ID',
        'Objeto',
        'Descrição',
        'IP',
        'Sucesso'
    ])
    
    # Dados
    for log in logs:
        writer.writerow([
            log.id,
            log.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
            log.usuario.username if log.usuario else 'Sistema',
            log.get_acao_display(),
            log.modelo or '',
            log.objeto_id or '',
            log.objeto_repr or '',
            log.descricao,
            log.ip_address or '',
            'Sim' if log.sucesso else 'Não'
        ])
    
    return response

@login_required
def lista_usuarios(request):
    """Lista todos os usuários do sistema"""
    # Apenas admin pode ver lista de usuários
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('os_app:index')
    
    # Busca e filtros
    usuarios = User.objects.select_related('perfil').all()
    
    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo:
        usuarios = usuarios.filter(perfil__tipo_usuario=tipo)
    
    # Filtro por status
    status = request.GET.get('status')
    if status == 'ativo':
        usuarios = usuarios.filter(is_active=True)
    elif status == 'inativo':
        usuarios = usuarios.filter(is_active=False)
    
    # Busca por nome/username
    busca = request.GET.get('busca')
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    usuarios = usuarios.order_by('-date_joined')
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    usuarios_admin = User.objects.filter(is_staff=True).count()
    
    context = {
        'page_obj': page_obj,
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'usuarios_admin': usuarios_admin,
        'tipo_choices': TIPO_USUARIO_CHOICES,
    }
    
    return render(request, 'os_app/usuarios/lista_usuarios.html', context)


@login_required
def novo_usuario(request):
    """Criar novo usuário"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('os_app:index')
    
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                
                # Registra log
                LogAuditoria.registrar(
                    usuario=request.user,
                    acao='CREATE',
                    modelo='Usuario',
                    objeto_id=user.id,
                    objeto_repr=user.username,
                    descricao=f'Criou novo usuário: {user.username}',
                    request=request
                )
                
                messages.success(request, f'Usuário {user.username} criado com sucesso!')
                return redirect('os_app:detalhe_usuario', user_id=user.id)
            except Exception as e:
                messages.error(request, f'Erro ao criar usuário: {str(e)}')
    else:
        form = UsuarioCreateForm()
    
    context = {
        'form': form,
        'titulo': 'Novo Usuário',
        'acao': 'criar'
    }
    
    return render(request, 'os_app/usuarios/form_usuario.html', context)


@login_required
def detalhe_usuario(request, user_id):
    """Visualizar detalhes do usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Usuário comum só pode ver próprio perfil
    if not request.user.is_staff and request.user != usuario:
        messages.error(request, "Você não tem permissão para ver este perfil.")
        return redirect('os_app:index')
    
    # Últimas ações do usuário
    ultimas_acoes = LogAuditoria.objects.filter(
        usuario=usuario
    ).order_by('-data_hora')[:10]
    
    context = {
        'usuario_detalhe': usuario,
        'perfil': usuario.perfil,
        'ultimas_acoes': ultimas_acoes,
    }
    
    return render(request, 'os_app/usuarios/detalhe_usuario.html', context)


@login_required
def editar_usuario(request, user_id):
    """Editar usuário existente"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Apenas admin pode editar outros usuários
    if not request.user.is_staff and request.user != usuario:
        messages.error(request, "Você não tem permissão para editar este usuário.")
        return redirect('os_app:index')
    
    if request.method == 'POST':
        user_form = UsuarioUpdateForm(request.POST, instance=usuario)
        perfil_form = PerfilUsuarioForm(
            request.POST, 
            request.FILES, 
            instance=usuario.perfil
        )
        
        if user_form.is_valid() and perfil_form.is_valid():
            try:
                user_form.save()
                perfil_form.save()
                
                # Registra log
                LogAuditoria.registrar(
                    usuario=request.user,
                    acao='UPDATE',
                    modelo='Usuario',
                    objeto_id=usuario.id,
                    objeto_repr=usuario.username,
                    descricao=f'Editou usuário: {usuario.username}',
                    request=request
                )
                
                messages.success(request, 'Usuário atualizado com sucesso!')
                return redirect('os_app:detalhe_usuario', user_id=usuario.id)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar usuário: {str(e)}')
    else:
        user_form = UsuarioUpdateForm(instance=usuario)
        perfil_form = PerfilUsuarioForm(instance=usuario.perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'usuario_edit': usuario,
        'titulo': f'Editar: {usuario.username}',
        'acao': 'editar'
    }
    
    return render(request, 'os_app/usuarios/form_usuario_editar.html', context)


@login_required
def alterar_senha(request, user_id):
    """Alterar senha do usuário"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Só pode alterar própria senha ou admin pode alterar de outros
    if not request.user.is_staff and request.user != usuario:
        messages.error(request, "Você não tem permissão para alterar esta senha.")
        return redirect('os_app:index')
    
    if request.method == 'POST':
        form = AlterarSenhaForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            
            # Mantém usuário logado se alterou própria senha
            if request.user == usuario:
                update_session_auth_hash(request, usuario)
            
            # Registra log
            LogAuditoria.registrar(
                usuario=request.user,
                acao='UPDATE',
                modelo='Usuario',
                objeto_id=usuario.id,
                objeto_repr=usuario.username,
                descricao=f'Alterou senha do usuário: {usuario.username}',
                request=request
            )
            
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('os_app:detalhe_usuario', user_id=usuario.id)
    else:
        form = AlterarSenhaForm(usuario)
    
    context = {
        'form': form,
        'usuario_senha': usuario,
    }
    
    return render(request, 'os_app/usuarios/alterar_senha.html', context)


@login_required
def desativar_usuario(request, user_id):
    """Desativar/Ativar usuário"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para esta ação.")
        return redirect('os_app:index')
    
    usuario = get_object_or_404(User, id=user_id)
    
    # Não pode desativar próprio usuário
    if usuario == request.user:
        messages.error(request, "Você não pode desativar seu próprio usuário!")
        return redirect('os_app:lista_usuarios')
    
    if request.method == 'POST':
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        status = 'ativado' if usuario.is_active else 'desativado'
        
        # Registra log
        LogAuditoria.registrar(
            usuario=request.user,
            acao='UPDATE',
            modelo='Usuario',
            objeto_id=usuario.id,
            objeto_repr=usuario.username,
            descricao=f'Usuário {status}: {usuario.username}',
            request=request
        )
        
        messages.success(request, f'Usuário {status} com sucesso!')
        return redirect('os_app:lista_usuarios')
    
    context = {
        'usuario_acao': usuario,
        'acao': 'desativar' if usuario.is_active else 'ativar'
    }
    
    return render(request, 'os_app/usuarios/confirmar_desativar.html', context)


@login_required
def meu_perfil(request):
    """Perfil do usuário logado"""
    return redirect('os_app:detalhe_usuario', user_id=request.user.id)


@login_required
def minha_senha(request):
    """Alterar própria senha"""
    return redirect('os_app:alterar_senha', user_id=request.user.id)
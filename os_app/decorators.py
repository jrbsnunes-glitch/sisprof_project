# os_app/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


# ============================================================================
# DECORATORS PARA PROFESSORES
# ============================================================================

def permissao_criar_professor(view_func):
    """Decorator para verificar permissão de criar professor"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para criar professores.")
            return redirect('os_app:lista_professores')
        
        # Verifica permissão
        if not request.user.perfil.pode_criar_professor:
            messages.error(request, "Você não tem permissão para criar professores.")
            return redirect('os_app:lista_professores')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_editar_professor(view_func):
    """Decorator para verificar permissão de editar professor"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para editar professores.")
            return redirect('os_app:lista_professores')
        
        # Verifica permissão
        if not request.user.perfil.pode_editar_professor:
            messages.error(request, "Você não tem permissão para editar professores.")
            return redirect('os_app:lista_professores')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_excluir_professor(view_func):
    """Decorator para verificar permissão de excluir professor"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para excluir professores.")
            return redirect('os_app:lista_professores')
        
        # Verifica permissão
        if not request.user.perfil.pode_excluir_professor:
            messages.error(request, "Você não tem permissão para excluir professores.")
            return redirect('os_app:lista_professores')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# DECORATORS PARA ESCOLAS NÚCLEO
# ============================================================================

def permissao_criar_escola_nucleo(view_func):
    """Decorator para verificar permissão de criar escola núcleo"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para criar escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        # Verifica permissão
        if not request.user.perfil.pode_criar_escola_nucleo:
            messages.error(request, "Você não tem permissão para criar escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_editar_escola_nucleo(view_func):
    """Decorator para verificar permissão de editar escola núcleo"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para editar escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        # Verifica permissão
        if not request.user.perfil.pode_editar_escola_nucleo:
            messages.error(request, "Você não tem permissão para editar escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_excluir_escola_nucleo(view_func):
    """Decorator para verificar permissão de excluir escola núcleo"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para excluir escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        # Verifica permissão
        if not request.user.perfil.pode_excluir_escola_nucleo:
            messages.error(request, "Você não tem permissão para excluir escolas núcleo.")
            return redirect('os_app:lista_escolas_nucleo')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# DECORATORS PARA ESCOLAS DEPENDENTES
# ============================================================================

def permissao_criar_escola_dependente(view_func):
    """Decorator para verificar permissão de criar escola dependente"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para criar escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        # Verifica permissão
        if not request.user.perfil.pode_criar_escola_dependente:
            messages.error(request, "Você não tem permissão para criar escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_editar_escola_dependente(view_func):
    """Decorator para verificar permissão de editar escola dependente"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para editar escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        # Verifica permissão
        if not request.user.perfil.pode_editar_escola_dependente:
            messages.error(request, "Você não tem permissão para editar escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_excluir_escola_dependente(view_func):
    """Decorator para verificar permissão de excluir escola dependente"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para excluir escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        # Verifica permissão
        if not request.user.perfil.pode_excluir_escola_dependente:
            messages.error(request, "Você não tem permissão para excluir escolas dependentes.")
            return redirect('os_app:lista_escolas_dependentes')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# DECORATORS GERAIS
# ============================================================================

def permissao_gerar_relatorios(view_func):
    """Decorator para verificar permissão de gerar relatórios"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para gerar relatórios.")
            return redirect('os_app:index')
        
        # Verifica permissão
        if not request.user.perfil.pode_gerar_relatorios:
            messages.error(request, "Você não tem permissão para gerar relatórios.")
            return redirect('os_app:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permissao_exportar_dados(view_func):
    """Decorator para verificar permissão de exportar dados"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Superusuário sempre pode
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verifica se tem perfil
        if not hasattr(request.user, 'perfil'):
            messages.error(request, "Você não tem permissão para exportar dados.")
            return redirect('os_app:index')
        
        # Verifica permissão
        if not request.user.perfil.pode_exportar_dados:
            messages.error(request, "Você não tem permissão para exportar dados.")
            return redirect('os_app:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper
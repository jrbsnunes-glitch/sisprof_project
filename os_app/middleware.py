# ============================================================================
# MIDDLEWARE DE AUDITORIA
# Arquivo: os_app/middleware.py (CRIAR ESTE ARQUIVO)
# ============================================================================

from django.utils.deprecation import MiddlewareMixin
from .models import LogAuditoria


class AuditoriaMiddleware(MiddlewareMixin):
    """
    Middleware que registra automaticamente ações dos usuários
    """
    
    def process_request(self, request):
        """Processa a requisição"""
        # Armazena o request para uso posterior
        request._auditoria_processada = False
        return None
    
    def process_response(self, request, response):
        """Processa a resposta"""
        # Só registra se usuário estiver autenticado
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Evita registrar requisições de arquivos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response
        
        # Evita registrar requisições AJAX de autocomplete
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return response
        
        # Registra apenas requisições bem-sucedidas (200-399)
        if response.status_code >= 400:
            return response
        
        # Evita duplicação
        if getattr(request, '_auditoria_processada', False):
            return response
        
        # Identifica a ação baseada no método e URL
        acao = self._identificar_acao(request)
        
        if acao:
            try:
                # Extrai informações da URL
                modelo, objeto_id = self._extrair_modelo_id(request.path)
                
                # Cria descrição
                descricao = self._criar_descricao(request, acao)
                
                # Registra log
                LogAuditoria.registrar(
                    usuario=request.user,
                    acao=acao,
                    modelo=modelo,
                    objeto_id=objeto_id,
                    descricao=descricao,
                    request=request,
                    sucesso=True
                )
                
                request._auditoria_processada = True
            except Exception as e:
                # Não quebra a aplicação se logging falhar
                print(f"Erro ao registrar log de auditoria: {e}")
        
        return response
    
    def _identificar_acao(self, request):
        """Identifica a ação baseada na requisição"""
        path = request.path
        method = request.method
        
        # Login/Logout
        if '/login/' in path and method == 'POST':
            return 'LOGIN'
        if '/logout/' in path:
            return 'LOGOUT'
        
        # CRUD
        if method == 'POST':
            if '/novo/' in path or '/criar/' in path:
                return 'CREATE'
            elif '/editar/' in path:
                return 'UPDATE'
        
        if method == 'GET':
            if '/detalhes/' in path or '/detalhe/' in path:
                return 'VIEW'
            elif '/relatorios/' in path or '/pdf/' in path:
                return 'REPORT'
            elif '/buscar/' in path or '/pesquisar/' in path:
                return 'SEARCH'
        
        # Não registra navegação comum
        return None
    
    def _extrair_modelo_id(self, path):
        """Extrai modelo e ID da URL"""
        modelo = None
        objeto_id = None
        
        if '/professores/' in path:
            modelo = 'Professor'
            # Tenta extrair ID
            import re
            match = re.search(r'/professores/(\d+)/', path)
            if match:
                objeto_id = int(match.group(1))
        
        elif '/escolas/' in path:
            modelo = 'Escola'
            match = re.search(r'/escolas/(\d+)/', path)
            if match:
                objeto_id = int(match.group(1))
        
        elif '/nucleos/' in path:
            modelo = 'EscolaNucleo'
            match = re.search(r'/nucleos/(\d+)/', path)
            if match:
                objeto_id = int(match.group(1))
        
        return modelo, objeto_id
    
    def _criar_descricao(self, request, acao):
        """Cria descrição legível da ação"""
        path = request.path
        
        if acao == 'LOGIN':
            return f"Login realizado de {request.META.get('REMOTE_ADDR', 'IP desconhecido')}"
        
        elif acao == 'LOGOUT':
            return "Logout do sistema"
        
        elif acao == 'CREATE':
            if 'professor' in path:
                return "Cadastro de novo professor"
            elif 'escola' in path:
                return "Cadastro de nova escola"
            return "Criação de novo registro"
        
        elif acao == 'UPDATE':
            if 'professor' in path:
                return "Atualização de dados do professor"
            elif 'escola' in path:
                return "Atualização de dados da escola"
            return "Atualização de registro"
        
        elif acao == 'VIEW':
            return "Visualização de detalhes"
        
        elif acao == 'REPORT':
            return "Geração de relatório"
        
        elif acao == 'SEARCH':
            return "Busca/filtro de registros"
        
        return f"Ação: {acao}"
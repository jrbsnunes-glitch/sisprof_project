from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Professor, EscolaNucleo, Escola, Cargo, Bairro, Serie, Motivo,
    PerfilUsuario, LogAuditoria
)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'cpf', 'ref_global', 'cargo', 'situacao_funcional', 
        'get_escola', 'em_sala', 'ativo'
    ]
    list_filter = [
        'ativo', 'em_sala', 'situacao_funcional', 'cargo',
        'escola_nucleo'
    ]
    search_fields = [
        'nome', 'cpf', 'matricula', 'email', 'telefone'
    ]
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    raw_id_fields = [
        'escola_lotacao', 'escola_nucleo', 'cargo', 'bairro', 
        'serie', 'motivo_fora_sala'
    ]
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': (
                'nome', 'cpf', 'ref_global', 'foto', 'telefone', 'email'
            )
        }),
        ('Dados Profissionais', {
            'fields': (
                'matricula', 'cargo', 'situacao_funcional', 'area_atuacao',
                'escola_nucleo', 'escola_lotacao'
            )
        }),
        ('Endereço Residencial', {
            'fields': (
                'bairro', 'numero', 'complemento'
            )
        }),
        ('Dados Acadêmicos', {
            'fields': (
                'modalidade', 'serie', 'turno', 'carga_horaria', 'disciplinas'
            )
        }),
        ('Situação Atual', {
            'fields': (
                'em_sala', 'motivo_fora_sala', 'observacoes'
            )
        }),
        ('Controle', {
            'fields': (
                'ativo', 'data_cadastro', 'data_atualizacao'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_escola(self, obj):
        """Exibe escola de lotação ou núcleo"""
        if obj.escola_lotacao:
            return obj.escola_lotacao.nome
        elif obj.escola_nucleo:
            return f"{obj.escola_nucleo.nome} (Núcleo)"
        return "-"
    get_escola.short_description = 'Escola'


@admin.register(EscolaNucleo)
class EscolaNucleoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'codigo', 'codigo_inep', 'cidade', 'estado', 
        'zona', 'data_cadastro'
    ]
    list_filter = ['zona', 'estado', 'cidade']
    search_fields = ['nome', 'codigo', 'codigo_inep', 'cidade']
    readonly_fields = ['data_cadastro']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'codigo_inep')
        }),
        ('Endereço', {
            'fields': (
                'endereco', 'numero', 'bairro', 'cep',
                'cidade', 'estado', 'zona'
            )
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Controle', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'nucleo', 'codigo_inep', 'cidade', 
        'estado', 'zona', 'data_cadastro'
    ]
    list_filter = ['zona', 'nucleo', 'estado', 'cidade']
    search_fields = ['nome', 'codigo_inep', 'cidade', 'nucleo__nome']
    readonly_fields = ['data_cadastro']
    raw_id_fields = ['nucleo', 'bairro']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nucleo', 'nome', 'codigo_inep')
        }),
        ('Endereço', {
            'fields': (
                'endereco', 'numero', 'bairro', 'cep',
                'cidade', 'estado', 'zona'
            )
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Controle', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'data_cadastro']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_cadastro']


@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'estado', 'data_cadastro']
    list_filter = ['estado', 'cidade']
    search_fields = ['nome', 'cidade']
    readonly_fields = ['data_cadastro']


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'data_cadastro']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_cadastro']


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'ativo', 'data_cadastro']
    list_filter = ['ativo']
    search_fields = ['descricao', 'observacoes']
    readonly_fields = ['data_cadastro']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'tipo_usuario', 'cargo_funcao', 
        'ativo', 'data_criacao'
    ]
    list_filter = ['ativo', 'tipo_usuario', 'data_criacao']
    search_fields = [
        'usuario__username', 'usuario__email', 
        'usuario__first_name', 'usuario__last_name',
        'cargo_funcao', 'departamento'
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    raw_id_fields = ['usuario', 'escola_vinculada', 'nucleo_vinculado']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Tipo e Função', {
            'fields': ('tipo_usuario', 'cargo_funcao', 'departamento')
        }),
        ('Vinculação', {
            'fields': ('escola_vinculada', 'nucleo_vinculado')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular', 'foto')
        }),
        ('Permissões - Professores', {
            'fields': (
                'pode_criar_professor',
                'pode_editar_professor',
                'pode_excluir_professor',
            ),
            'classes': ('collapse',)
        }),
        ('Permissões - Escolas Núcleo', {
            'fields': (
                'pode_criar_escola_nucleo',
                'pode_editar_escola_nucleo',
                'pode_excluir_escola_nucleo',
            ),
            'classes': ('collapse',)
        }),
        ('Permissões - Escolas Dependentes', {
            'fields': (
                'pode_criar_escola_dependente',
                'pode_editar_escola_dependente',
                'pode_excluir_escola_dependente',
            ),
            'classes': ('collapse',)
        }),
        ('Permissões Gerais', {
            'fields': (
                'pode_gerar_relatorios',
                'pode_exportar_dados',
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo', 'observacoes')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'data_hora', 'usuario', 'acao', 'modelo', 
        'objeto_repr', 'sucesso', 'ip_address'
    ]
    list_filter = [
        'acao', 'modelo', 'sucesso', 'data_hora'
    ]
    search_fields = [
        'usuario__username', 'descricao', 'objeto_repr',
        'ip_address'
    ]
    readonly_fields = [
        'usuario', 'acao', 'modelo', 'objeto_id', 'objeto_repr',
        'descricao', 'dados_anteriores', 'dados_novos',
        'ip_address', 'user_agent', 'data_hora', 'sucesso',
        'mensagem_erro'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'data_hora', 'usuario', 'acao', 'modelo', 
                'objeto_id', 'objeto_repr'
            )
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Dados', {
            'fields': ('dados_anteriores', 'dados_novos'),
            'classes': ('collapse',)
        }),
        ('Contexto', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Resultado', {
            'fields': ('sucesso', 'mensagem_erro')
        }),
    )
    
    def has_add_permission(self, request):
        """Logs não podem ser adicionados manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs não podem ser editados"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Apenas superusuários podem deletar logs"""
        return request.user.is_superuser


# Customização do Django Admin
admin.site.site_header = "SISPROF - Administração"
admin.site.site_title = "SISPROF Admin"
admin.site.index_title = "Painel de Administração"
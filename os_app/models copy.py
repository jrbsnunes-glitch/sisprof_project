from django.db import models
import re
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




AREA_ATUACAO_CHOICES = [
    ('', 'Selecione uma área'),
    ('lingua_portuguesa', 'Língua Portuguesa'),
    ('matematica', 'Matemática'),
    ('historia', 'História'),
    ('geografia', 'Geografia'),
    ('ciencias', 'Ciências'),
    ('fisica', 'Física'),
    ('quimica', 'Química'),
    ('biologia', 'Biologia'),
    ('educacao_fisica', 'Educação Física'),
    ('arte', 'Arte'),
    ('lingua_estrangeira_ingles', 'Língua Estrangeira - Inglês'),
    ('lingua_estrangeira_espanhol', 'Língua Estrangeira - Espanhol'),
    ('ensino_religioso', 'Ensino Religioso'),
    ('filosofia', 'Filosofia'),
    ('sociologia', 'Sociologia'),
    ('literatura', 'Literatura'),
    ('redacao', 'Redação'),
    ('educacao_infantil', 'Educação Infantil'),
    ('anos_iniciais_ef', 'Anos Iniciais do Ensino Fundamental'),
    ('anos_finais_ef', 'Anos Finais do Ensino Fundamental'),
    ('ensino_medio', 'Ensino Médio'),
    ('gestao_escolar', 'Gestão Escolar'),
    ('coordenacao_pedagogica', 'Coordenação Pedagógica'),
    ('biblioteconomia', 'Biblioteconomia'),
    ('psicologia_escolar', 'Psicologia Escolar'),
    ('outras', 'Outras'),
]

SITUACAO_FUNCIONAL_CHOICES = [
    ('', 'Selecione'),
    ('acrescimo', 'Acréscimo'),
    ('contratado', 'Contratado'),
    ('dobra', 'Dobra'),
    ('efetivo', 'Efetivo'),
]

MODALIDADE_CHOICES = [
    ('', 'Selecione'),
    ('ed_esp', 'Ed. Esp'),
    ('ed_inf', 'Ed. Inf'),
    ('eja', 'EJA'),
    ('fund_1', 'Fund 1'),
    ('fund_2', 'Fund 2'),
    ('ind', 'Ind'),
    ('fund', 'Fund'),
]

TURNO_CHOICES = [
    ('', 'Selecione'),
    ('diurno', 'Diurno'),
    ('matutino', 'Matutino'),
    ('vespertino', 'Vespertino'),
    ('noturno', 'Noturno'),
]

ZONA_CHOICES = [
    ('rural', 'Rural'),
    ('urbana', 'Urbana'),
]

MATERIAS_CHOICES = [
    ('portugues', 'Português'),
    ('matematica', 'Matemática'),
    ('historia', 'História'),
    ('geografia', 'Geografia'),
    ('ciencias', 'Ciências'),
    ('educacao_fisica', 'Ed. Física'),
    ('artes', 'Artes'),
    ('ensino_religioso', 'Ens. Religioso'),
    ('ingles', 'Inglês'),
]

TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('COORDENADOR', 'Coordenador'),
        ('CONSULTA', 'Apenas Consulta'),
    ]


class EscolaNucleo(models.Model):
    """Escola Principal/Núcleo - Nível superior na hierarquia"""
    nome = models.CharField('Nome do Núcleo', max_length=200)
    codigo = models.CharField('Código', max_length=20, blank=True, null=True, unique=True)
    codigo_inep = models.CharField('Código INEP', max_length=8, blank=True, null=True, unique=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=20, blank=True)
    bairro = models.ForeignKey('Bairro', on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Bairro', related_name='escolas_nucleo')
    cep = models.CharField('CEP', max_length=9, blank=True)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    zona = models.CharField('Zona', max_length=10, choices=ZONA_CHOICES, default='urbana')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Escola Núcleo'
        verbose_name_plural = 'Escolas Núcleo'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Escola(models.Model):
    """Escola de Lotação - Vinculada a uma Escola Núcleo"""
    nucleo = models.ForeignKey(
        EscolaNucleo, 
        on_delete=models.CASCADE, 
        related_name='escolas_lotacao',
        verbose_name='Escola Núcleo',
        null=True,
        blank=True
    )
    nome = models.CharField('Nome da Escola', max_length=200)
    codigo_inep = models.CharField('Código INEP', max_length=8, blank=True, null=True, unique=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=20, blank=True)
    bairro = models.ForeignKey('Bairro', on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Bairro', related_name='escolas_dependentes')
    cep = models.CharField('CEP', max_length=9, blank=True)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    zona = models.CharField('Zona', max_length=10, choices=ZONA_CHOICES, default='urbana')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Escola de Lotação'
        verbose_name_plural = 'Escolas de Lotação'
        ordering = ['nome']

    def __str__(self):
        if self.nucleo:
            return f"{self.nome} ({self.nucleo.nome})"
        return self.nome
    
    def nome_completo(self):
        """Retorna nome completo com núcleo"""
        if self.nucleo:
            return f"{self.nome} - Núcleo: {self.nucleo.nome}"
        return self.nome


class Cargo(models.Model):
    """Cargo do Professor"""
    nome = models.CharField('Nome do Cargo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Bairro(models.Model):
    """Bairro - Compartilhado entre múltiplos cadastros"""
    nome = models.CharField('Nome do Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Bairro'
        verbose_name_plural = 'Bairros'
        ordering = ['nome']
        unique_together = ['nome', 'cidade', 'estado']  # Evita duplicação

    def __str__(self):
        if self.cidade and self.estado:
            return f"{self.nome} - {self.cidade}/{self.estado}"
        elif self.cidade:
            return f"{self.nome} - {self.cidade}"
        return self.nome


class Serie(models.Model):
    """Série/Ano Escolar"""
    nome = models.CharField('Nome da Série', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Série'
        verbose_name_plural = 'Séries'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Motivo(models.Model):
    """Motivo de não estar em sala"""
    descricao = models.CharField('Descrição', max_length=200, unique=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Motivo'
        verbose_name_plural = 'Motivos'
        ordering = ['descricao']

    def __str__(self):
        return self.descricao


class Professor(models.Model):
    # Dados Pessoais
    nome = models.CharField('Nome Completo', max_length=100)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    ref_global = models.CharField('Ref. Global', max_length=5, blank=True, null=True)
    foto = models.ImageField('Foto', upload_to='professores/fotos/', null=True, blank=True, 
                             help_text='Foto do professor (opcional)')
    telefone = models.CharField('Telefone', max_length=15)
    email = models.EmailField('E-mail')
    
    # Dados Profissionais
    matricula = models.CharField('Matrícula', max_length=20, unique=True, blank=True, null=True)
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cargo'
    )
    situacao_funcional = models.CharField('Situação Funcional', max_length=20, 
                                         choices=SITUACAO_FUNCIONAL_CHOICES, blank=True)
    area_atuacao = models.CharField('Área de Atuação', max_length=50, 
                                    choices=AREA_ATUACAO_CHOICES, blank=True)
    materias = models.TextField(
        'Matérias',
        blank=True,
        default='',
        help_text='Matérias que o professor leciona (separadas por vírgula)'
    )
    escola = models.ForeignKey(
        Escola, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Escola de Lotação'
    )
    escola_nucleo = models.ForeignKey(
        EscolaNucleo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Escola Núcleo (caso não tenha dependente)',
        help_text='Use este campo se o professor está lotado direto no núcleo'
    )
    
    # Endereço
    endereco = models.CharField('Endereço', max_length=150)
    numero = models.CharField('Número', max_length=20, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)
    bairro = models.ForeignKey('Bairro', on_delete=models.SET_NULL, null=True, blank=True, 
                               verbose_name='Bairro')
    cidade = models.CharField('Cidade', max_length=50)
    estado = models.CharField('Estado', max_length=2)
    
    # Dados de Turmas
    modalidade = models.CharField('Modalidade', max_length=20, choices=MODALIDADE_CHOICES, blank=True)
    serie = models.ForeignKey(Serie, on_delete=models.SET_NULL, null=True, blank=True, 
                             verbose_name='Série')
    turno = models.CharField('Turno', max_length=20, choices=TURNO_CHOICES, blank=True)
    em_sala = models.CharField('Em Sala', max_length=3, choices=[('sim', 'SIM'), ('nao', 'NÃO')], 
                               blank=True)
    motivo = models.ForeignKey(Motivo, on_delete=models.SET_NULL, null=True, blank=True, 
                              verbose_name='Motivo')
    substituto = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='substituindo', verbose_name='Substituto')
    observacao_turmas = models.TextField('Observação sobre Turmas', blank=True)
    
    # Metadata
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    def get_escola_lotacao(self):
        """Retorna a escola de lotação (dependente ou núcleo)"""
        if self.escola:
            return self.escola.nome
        elif self.escola_nucleo:
            return f"{self.escola_nucleo.nome} (Núcleo)"
        return "Não informado"
    
    def cpf_formatado(self):
        """Retorna CPF formatado"""
        cpf_numeros = re.sub(r'\D', '', self.cpf)
        if len(cpf_numeros) == 11:
            return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        return self.cpf
    
    def get_materias_list(self):
        """Retorna lista de matérias"""
        if not self.materias:
            return []
        return [m.strip() for m in self.materias.split(',') if m.strip()]
    
    def set_materias_list(self, materias_list):
        """Define matérias a partir de uma lista"""
        self.materias = ','.join(materias_list) if materias_list else ''
    
    def get_materias_display(self):
        """Retorna matérias formatadas para exibição"""
        materias_dict = dict(MATERIAS_CHOICES)
        materias_list = self.get_materias_list()
        return [materias_dict.get(m, m) for m in materias_list]
    
class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('COORDENADOR', 'Coordenador'),
        ('CONSULTA', 'Apenas Consulta'),
    ]
    """Perfil estendido do usuário com informações adicionais"""
    # Vínculo com usuário do Django
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuário'
    )
    
    # Informações profissionais
    tipo_usuario = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='CONSULTA'
    )
    
    cargo_funcao = models.CharField(
        'Cargo/Função',
        max_length=100,
        blank=True
    )
    
    departamento = models.CharField(
        'Departamento',
        max_length=100,
        blank=True
    )
    
    # Escola/Núcleo vinculado (opcional)
    escola_vinculada = models.ForeignKey(
        'Escola',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Escola Vinculada',
        help_text='Escola à qual o usuário está vinculado'
    )
    
    nucleo_vinculado = models.ForeignKey(
        'EscolaNucleo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Núcleo Vinculado',
        help_text='Núcleo ao qual o usuário está vinculado'
    )
    
    # Contato
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True
    )
    
    celular = models.CharField(
        'Celular',
        max_length=20,
        blank=True
    )
    
    # Foto
    foto = models.ImageField(
        'Foto',
        upload_to='usuarios/',
        blank=True,
        null=True
    )
    
    # Permissões específicas
    pode_criar_professor = models.BooleanField(
        'Pode Criar Professores',
        default=False
    )
    
    pode_editar_professor = models.BooleanField(
        'Pode Editar Professores',
        default=False
    )
    
    pode_excluir_professor = models.BooleanField(
        'Pode Excluir Professores',
        default=False
    )
    
    pode_gerar_relatorios = models.BooleanField(
        'Pode Gerar Relatórios',
        default=True
    )
    
    pode_exportar_dados = models.BooleanField(
        'Pode Exportar Dados',
        default=False
    )
    
    # Status e controle
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Usuário pode acessar o sistema'
    )
    
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )
    
    ultimo_acesso = models.DateTimeField(
        'Último Acesso',
        null=True,
        blank=True
    )
    
    observacoes = models.TextField(
        'Observações',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        ordering = ['usuario__username']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_usuario_display()}"
    
    @property
    def nome_completo(self):
        """Retorna nome completo ou username"""
        return self.usuario.get_full_name() or self.usuario.username
    
    @property
    def email(self):
        """Retorna email do usuário"""
        return self.usuario.email
    
    def tem_permissao(self, permissao):
        """Verifica se usuário tem permissão específica"""
        # Admin sempre tem todas as permissões
        if self.usuario.is_superuser or self.tipo_usuario == 'ADMIN':
            return True
        
        permissoes_map = {
            'criar_professor': self.pode_criar_professor,
            'editar_professor': self.pode_editar_professor,
            'excluir_professor': self.pode_excluir_professor,
            'gerar_relatorios': self.pode_gerar_relatorios,
            'exportar_dados': self.pode_exportar_dados,
        }
        
        return permissoes_map.get(permissao, False)


# ============================================================================
# SIGNALS - Criar perfil automaticamente ao criar usuário
# ============================================================================

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """Cria perfil automaticamente quando usuário é criado"""
    if created:
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    """Salva perfil quando usuário é salvo"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    
# ============================================================================
# MODELO DE LOG DE AUDITORIA

# ============================================================================

class LogAuditoria(models.Model):
    """
    Registra todas as ações dos usuários no sistema
    """
    ACAO_CHOICES = [
        ('LOGIN', 'Login no Sistema'),
        ('LOGOUT', 'Logout do Sistema'),
        ('CREATE', 'Criação de Registro'),
        ('UPDATE', 'Atualização de Registro'),
        ('DELETE', 'Exclusão de Registro'),
        ('VIEW', 'Visualização de Registro'),
        ('SEARCH', 'Busca/Filtro'),
        ('EXPORT', 'Exportação de Dados'),
        ('IMPORT', 'Importação de Dados'),
        ('REPORT', 'Geração de Relatório'),
        ('PRINT', 'Impressão de Documento'),
    ]
    
    MODELO_CHOICES = [
        ('Professor', 'Professor'),
        ('Escola', 'Escola'),
        ('EscolaNucleo', 'Escola Núcleo'),
        ('Cargo', 'Cargo'),
        ('Bairro', 'Bairro'),
        ('Serie', 'Série'),
        ('Motivo', 'Motivo'),
        ('Usuario', 'Usuário'),
        ('Sistema', 'Sistema'),
    ]
    
    # Quem fez a ação
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuário',
        related_name='logs'
    )
    
    # O que foi feito
    acao = models.CharField(
        'Ação',
        max_length=20,
        choices=ACAO_CHOICES
    )
    
    # Em qual modelo
    modelo = models.CharField(
        'Modelo',
        max_length=50,
        choices=MODELO_CHOICES,
        null=True,
        blank=True
    )
    
    # ID do registro afetado
    objeto_id = models.IntegerField(
        'ID do Objeto',
        null=True,
        blank=True
    )
    
    # Representação do objeto (para histórico)
    objeto_repr = models.CharField(
        'Representação do Objeto',
        max_length=500,
        null=True,
        blank=True
    )
    
    # Descrição detalhada
    descricao = models.TextField(
        'Descrição',
        blank=True
    )
    
    # Dados anteriores (JSON)
    dados_anteriores = models.JSONField(
        'Dados Anteriores',
        null=True,
        blank=True,
        help_text='Estado anterior do registro (para UPDATE/DELETE)'
    )
    
    # Dados novos (JSON)
    dados_novos = models.JSONField(
        'Dados Novos',
        null=True,
        blank=True,
        help_text='Estado novo do registro (para CREATE/UPDATE)'
    )
    
    # Informações de contexto
    ip_address = models.GenericIPAddressField(
        'Endereço IP',
        null=True,
        blank=True
    )
    
    user_agent = models.CharField(
        'User Agent',
        max_length=500,
        blank=True,
        help_text='Navegador/dispositivo utilizado'
    )
    
    # Quando aconteceu
    data_hora = models.DateTimeField(
        'Data/Hora',
        auto_now_add=True
    )
    
    # Sucesso ou erro?
    sucesso = models.BooleanField(
        'Sucesso',
        default=True
    )
    
    mensagem_erro = models.TextField(
        'Mensagem de Erro',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['-data_hora']),
            models.Index(fields=['usuario', '-data_hora']),
            models.Index(fields=['acao', '-data_hora']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]
    
    def __str__(self):
        usuario_nome = self.usuario.username if self.usuario else 'Sistema'
        return f"{usuario_nome} - {self.get_acao_display()} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar(cls, usuario, acao, modelo=None, objeto_id=None, objeto_repr=None,
                  descricao='', dados_anteriores=None, dados_novos=None,
                  request=None, sucesso=True, mensagem_erro=''):
        """
        Método auxiliar para registrar logs facilmente
        
        Uso:
            LogAuditoria.registrar(
                usuario=request.user,
                acao='CREATE',
                modelo='Professor',
                objeto_id=professor.id,
                objeto_repr=str(professor),
                descricao='Cadastro de novo professor',
                dados_novos={'nome': 'João', 'cpf': '123.456.789-00'},
                request=request
            )
        """
        # Extrai IP e User Agent do request
        ip_address = None
        user_agent = ''
        
        if request:
            # Pega IP (considerando proxy)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Pega User Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Cria o log
        return cls.objects.create(
            usuario=usuario,
            acao=acao,
            modelo=modelo,
            objeto_id=objeto_id,
            objeto_repr=objeto_repr,
            descricao=descricao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            ip_address=ip_address,
            user_agent=user_agent,
            sucesso=sucesso,
            mensagem_erro=mensagem_erro
        )
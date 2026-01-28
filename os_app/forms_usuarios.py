# os_app/forms_usuarios.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario


# Choices definidas aqui para garantir compatibilidade
TIPO_USUARIO_CHOICES = [
    ('ADMIN', 'Administrador'),
    ('GESTOR', 'Gestor'),
    ('COORDENADOR', 'Coordenador'),
    ('CONSULTA', 'Apenas Consulta'),
]


class UsuarioCreateForm(UserCreationForm):
    """Form para criar novo usuário"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    tipo_usuario = forms.ChoiceField(
        label='Tipo de Usuário',
        choices=TIPO_USUARIO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    cargo_funcao = forms.CharField(
        label='Cargo/Função',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    departamento = forms.CharField(
        label='Departamento',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    telefone = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    celular = forms.CharField(
        label='Celular',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    foto = forms.ImageField(
        label='Foto',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    # Permissões - Professores
    pode_criar_professor = forms.BooleanField(
        label='Pode Criar Professores',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_editar_professor = forms.BooleanField(
        label='Pode Editar Professores',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_excluir_professor = forms.BooleanField(
        label='Pode Excluir Professores',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Permissões - Escolas Núcleo
    pode_criar_escola_nucleo = forms.BooleanField(
        label='Pode Criar Escolas Núcleo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_editar_escola_nucleo = forms.BooleanField(
        label='Pode Editar Escolas Núcleo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_excluir_escola_nucleo = forms.BooleanField(
        label='Pode Excluir Escolas Núcleo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Permissões - Escolas Dependentes
    pode_criar_escola_dependente = forms.BooleanField(
        label='Pode Criar Escolas Dependentes',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_editar_escola_dependente = forms.BooleanField(
        label='Pode Editar Escolas Dependentes',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_excluir_escola_dependente = forms.BooleanField(
        label='Pode Excluir Escolas Dependentes',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Permissões Gerais
    pode_gerar_relatorios = forms.BooleanField(
        label='Pode Gerar Relatórios',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pode_exportar_dados = forms.BooleanField(
        label='Pode Exportar Dados',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_staff = forms.BooleanField(
        label='Acesso ao Admin',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    observacoes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'password1', 'password2', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar Senha'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data.get('is_staff', False)
        
        if commit:
            user.save()
            
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.tipo_usuario = self.cleaned_data['tipo_usuario']
            perfil.cargo_funcao = self.cleaned_data.get('cargo_funcao', '')
            perfil.departamento = self.cleaned_data.get('departamento', '')
            perfil.telefone = self.cleaned_data.get('telefone', '')
            perfil.celular = self.cleaned_data.get('celular', '')
            
            # Permissões - Professores
            perfil.pode_criar_professor = self.cleaned_data.get('pode_criar_professor', False)
            perfil.pode_editar_professor = self.cleaned_data.get('pode_editar_professor', False)
            perfil.pode_excluir_professor = self.cleaned_data.get('pode_excluir_professor', False)
            
            # Permissões - Escolas Núcleo
            perfil.pode_criar_escola_nucleo = self.cleaned_data.get('pode_criar_escola_nucleo', False)
            perfil.pode_editar_escola_nucleo = self.cleaned_data.get('pode_editar_escola_nucleo', False)
            perfil.pode_excluir_escola_nucleo = self.cleaned_data.get('pode_excluir_escola_nucleo', False)
            
            # Permissões - Escolas Dependentes
            perfil.pode_criar_escola_dependente = self.cleaned_data.get('pode_criar_escola_dependente', False)
            perfil.pode_editar_escola_dependente = self.cleaned_data.get('pode_editar_escola_dependente', False)
            perfil.pode_excluir_escola_dependente = self.cleaned_data.get('pode_excluir_escola_dependente', False)
            
            # Permissões Gerais
            perfil.pode_gerar_relatorios = self.cleaned_data.get('pode_gerar_relatorios', True)
            perfil.pode_exportar_dados = self.cleaned_data.get('pode_exportar_dados', False)
            
            perfil.observacoes = self.cleaned_data.get('observacoes', '')
            
            if self.cleaned_data.get('foto'):
                perfil.foto = self.cleaned_data['foto']
            
            perfil.save()
        
        return user


class UsuarioUpdateForm(forms.ModelForm):
    """Form para editar usuário existente"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    is_active = forms.BooleanField(
        label='Ativo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_staff = forms.BooleanField(
        label='Acesso ao Admin',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PerfilUsuarioForm(forms.ModelForm):
    """Form para editar perfil do usuário"""
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'tipo_usuario', 'cargo_funcao', 'departamento',
            'escola_vinculada', 'nucleo_vinculado',
            'telefone', 'celular', 'foto',
            # Permissões - Professores
            'pode_criar_professor', 'pode_editar_professor', 'pode_excluir_professor',
            # Permissões - Escolas Núcleo
            'pode_criar_escola_nucleo', 'pode_editar_escola_nucleo', 'pode_excluir_escola_nucleo',
            # Permissões - Escolas Dependentes
            'pode_criar_escola_dependente', 'pode_editar_escola_dependente', 'pode_excluir_escola_dependente',
            # Permissões Gerais
            'pode_gerar_relatorios', 'pode_exportar_dados',
            'ativo', 'observacoes'
        ]
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'cargo_funcao': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'escola_vinculada': forms.Select(attrs={'class': 'form-select'}),
            'nucleo_vinculado': forms.Select(attrs={'class': 'form-select'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            # Permissões - Professores
            'pode_criar_professor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_editar_professor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_excluir_professor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Permissões - Escolas Núcleo
            'pode_criar_escola_nucleo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_editar_escola_nucleo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_excluir_escola_nucleo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Permissões - Escolas Dependentes
            'pode_criar_escola_dependente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_editar_escola_dependente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_excluir_escola_dependente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Permissões Gerais
            'pode_gerar_relatorios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_exportar_dados': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AlterarSenhaForm(forms.Form):
    """Form para alterar senha do usuário"""
    
    senha_atual = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    senha_nova = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    
    senha_confirmacao = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_senha_atual(self):
        senha_atual = self.cleaned_data.get('senha_atual')
        if not self.user.check_password(senha_atual):
            raise forms.ValidationError('Senha atual incorreta')
        return senha_atual
    
    def clean(self):
        cleaned_data = super().clean()
        senha_nova = cleaned_data.get('senha_nova')
        senha_confirmacao = cleaned_data.get('senha_confirmacao')
        
        if senha_nova and senha_confirmacao:
            if senha_nova != senha_confirmacao:
                raise forms.ValidationError('As senhas não coincidem')
        
        return cleaned_data
    
    def save(self):
        self.user.set_password(self.cleaned_data['senha_nova'])
        self.user.save()
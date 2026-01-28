from django import forms
from .models import (Professor, EscolaNucleo, Escola, Cargo, Bairro, Serie, Motivo,
                    AREA_ATUACAO_CHOICES, SITUACAO_FUNCIONAL_CHOICES, MODALIDADE_CHOICES, 
                    TURNO_CHOICES, MATERIAS_CHOICES)
import re
from django.contrib.auth.forms import AuthenticationForm


class ProfessorForm(forms.ModelForm):
    """Formulário para cadastro e edição de Professor"""
    
    nucleo = forms.ModelChoiceField(
        queryset=EscolaNucleo.objects.all(),
        required=False,
        empty_label="Selecione um núcleo",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_nucleo'}),
        label='Escola Núcleo'
    )

    materias_selecionadas = forms.MultipleChoiceField(
        label='Matérias',
        choices=MATERIAS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input materias-checkbox'
        }),
        help_text='Selecione todas as matérias que o professor leciona'
    )
    
    class Meta:
        model = Professor
        fields = [
            'nome', 'cpf', 'ref_global', 'foto', 'telefone', 'email',
            'matricula', 'cargo', 'situacao_funcional', 'area_atuacao', 
            'escola_lotacao', 'escola_nucleo',
            'bairro', 'numero', 'complemento',
            'modalidade', 'serie', 'turno', 'carga_horaria',
            'em_sala', 'motivo_fora_sala',
            'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '14',
                'placeholder': '000.000.000-00'
            }),
            'ref_global': forms.TextInput(attrs={
                'class': 'form-control text-center fw-bold',
                'maxlength': '5',
                'placeholder': '5 CHAR',
                'style': 'text-transform: uppercase; letter-spacing: 2px;'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_foto'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@exemplo.com'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Matrícula (opcional)'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_cargo'
            }),
            'situacao_funcional': forms.Select(attrs={
                'class': 'form-control'
            }),
            'area_atuacao': forms.Select(attrs={
                'class': 'form-control'
            }),
            'escola_lotacao': forms.Select(attrs={
                'class': 'form-control', 
                'id': 'id_escola_lotacao'
            }),
            'escola_nucleo': forms.HiddenInput(attrs={
                'id': 'id_escola_nucleo'
            }),
            'bairro': forms.HiddenInput(attrs={
                'id': 'id_bairro'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nº'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Complemento (opcional)'
            }),
            'modalidade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'serie': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_serie'
            }),
            'turno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 40',
                'min': '0'
            }),
            'em_sala': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'motivo_fora_sala': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_motivo_fora_sala'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Digite observações adicionais...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['escola_lotacao'].queryset = Escola.objects.select_related('nucleo').order_by('nucleo__nome', 'nome')
        
        if self.instance.pk and self.instance.escola_lotacao:
            self.fields['nucleo'].initial = self.instance.escola_lotacao.nucleo
        
        if self.instance.pk and self.instance.escola_nucleo:
            self.fields['nucleo'].initial = self.instance.escola_nucleo

        if self.instance and self.instance.pk and self.instance.disciplinas:
            materias_list = [m.strip() for m in self.instance.disciplinas.split(',') if m.strip()]
            self.fields['materias_selecionadas'].initial = materias_list

    def save(self, commit=True):
        professor = super().save(commit=False) 

        materias_list = self.cleaned_data.get('materias_selecionadas', [])
        if materias_list:
            professor.disciplinas = ', '.join(materias_list)
        else:
            professor.disciplinas = ''
        
        if commit:
            professor.save()
        
        return professor           

    def clean(self):
        cleaned_data = super().clean()
        escola_lotacao = cleaned_data.get('escola_lotacao')
        escola_nucleo = cleaned_data.get('escola_nucleo')
        nucleo = cleaned_data.get('nucleo')
        
        if escola_lotacao and escola_lotacao.nucleo:
            cleaned_data['escola_nucleo'] = escola_lotacao.nucleo
        elif nucleo and not escola_lotacao:
            cleaned_data['escola_nucleo'] = nucleo
            cleaned_data['escola_lotacao'] = None
        
        return cleaned_data

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_numeros = re.sub(r'\D', '', cpf)

        if len(cpf_numeros) != 11:
            raise forms.ValidationError("CPF deve ter 11 dígitos.")

        qs = Professor.objects.filter(cpf=cpf_numeros)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este CPF já está cadastrado.")

        return cpf_numeros
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        
        if foto:
            if hasattr(foto, 'content_type'):
                if foto.size > 5 * 1024 * 1024:
                    raise forms.ValidationError("A foto não pode ter mais de 5MB.")
                
                if not foto.content_type.startswith('image'):
                    raise forms.ValidationError("O arquivo deve ser uma imagem.")
        
        return foto


class EscolaNucleoForm(forms.ModelForm):
    """Formulário para cadastro de Escola Núcleo"""
    class Meta:
        model = EscolaNucleo
        fields = ['nome', 'codigo', 'codigo_inep', 'endereco', 'numero', 'bairro', 'cep', 
                 'cidade', 'estado', 'zona', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome do núcleo', 
                'required': True
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Código (opcional)'
            }),
            'codigo_inep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000000',
                'maxlength': '8'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Endereço'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº'
            }),
            'bairro': forms.HiddenInput(attrs={
                'id': 'id_nucleo_bairro'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'maxlength': '9'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Cidade', 
                'required': True
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'UF', 
                'maxlength': '2', 
                'required': True
            }),
            'zona': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@nucleo.com'
            }),
        }


class EscolaForm(forms.ModelForm):
    """Formulário para cadastro de Escola de Lotação via AJAX"""
    
    class Meta:
        model = Escola
        fields = ['nucleo', 'nome', 'codigo_inep', 'endereco', 'numero', 'bairro', 'cep',
                 'cidade', 'estado', 'zona', 'telefone', 'email']
        widgets = {
            'nucleo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome da escola', 
                'required': True
            }),
            'codigo_inep': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Código INEP (opcional)', 
                'maxlength': '8'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Endereço'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº'
            }),
            'bairro': forms.HiddenInput(attrs={
                'id': 'id_escola_bairro'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'maxlength': '9'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Cidade', 
                'required': True
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'UF', 
                'maxlength': '2', 
                'required': True
            }),
            'zona': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@escola.com'
            }),
        }


class CargoForm(forms.ModelForm):
    """Formulário para cadastro de Cargo via AJAX"""
    class Meta:
        model = Cargo
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Professor Efetivo', 
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do cargo (opcional)'
            }),
        }


class BairroForm(forms.ModelForm):
    """Formulário para cadastro de Bairro via AJAX"""
    
    class Meta:
        model = Bairro
        fields = ['nome', 'cidade', 'estado']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome do bairro', 
                'required': True
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Cidade (opcional)'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'UF', 
                'maxlength': '2'
            }),
        }


class SerieForm(forms.ModelForm):
    """Formulário para cadastro de Série via AJAX"""
    
    class Meta:
        model = Serie
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1º Ano, 2º Ano, etc.',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descrição adicional (opcional)'
            }),
        }


class MotivoForm(forms.ModelForm):
    """Formulário para cadastro de Motivo via AJAX"""
    
    class Meta:
        model = Motivo
        fields = ['descricao', 'observacoes']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Licença Médica, Afastamento, etc.',
                'required': True
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações adicionais (opcional)'
            }),
        }


class LoginForm(AuthenticationForm):
    """Formulário de login customizado"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuário',
            'autofocus': True
        }),
        label='Usuário'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        }),
        label='Senha'
    ) 
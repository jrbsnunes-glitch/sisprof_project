# 📚 SISPROF - Sistema de Gestão de Professores

Sistema completo para gerenciamento e cadastro de professores, desenvolvido em Django.

## 🚀 Funcionalidades

### ✅ Implementadas
- **Dashboard Interativo** com estatísticas em tempo real
- **Gerenciamento Completo de Professores** (CRUD)
  - Cadastro de professores com dados pessoais e profissionais
  - Visualização detalhada de cada professor
  - Edição de informações
  - Exclusão com confirmação
- **Gestão de Escolas e Bairros**
  - Cadastro via AJAX (sem sair da página)
  - Associação automática aos professores
- **Sistema de Login/Logout** com autenticação
- **Busca e Filtros Avançados**
  - Busca por nome, CPF, matrícula ou email
  - Filtro por escola
  - Filtro por área de atuação
  - Filtro por cidade
- **Busca de CEP Automática** (integração com ViaCEP)
- **Interface Moderna e Responsiva** com Bootstrap 5
- **Estatísticas no Dashboard**
  - Total de professores
  - Professores por escola
  - Professores por área de atuação
  - Últimos cadastros

## 📋 Pré-requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd sisprof_project
```

### 2. Crie e ative um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

**Requirements.txt necessário:**
```
Django==5.2
django-widget-tweaks
```

### 4. Configure o banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor
```bash
python manage.py runserver
```

### 7. Acesse o sistema
```
http://localhost:8000/os/
```

## 📁 Estrutura do Projeto

```
sisprof_project/
├── os_app/
│   ├── templates/
│   │   └── os_app/
│   │       ├── base.html              # Template base
│   │       ├── index.html             # Dashboard
│   │       ├── lista_professores.html # Lista com filtros
│   │       ├── novo_professor.html    # Cadastro/Edição
│   │       ├── detalhe_professor.html # Detalhes completos
│   │       ├── confirmar_delete.html  # Confirmação de exclusão
│   │       └── login.html             # Tela de login
│   ├── models.py                      # Modelos do banco
│   ├── views.py                       # Lógica das views
│   ├── forms.py                       # Formulários
│   ├── urls.py                        # Rotas da app
│   └── admin.py                       # Admin Django
├── sisprof_project/
│   ├── settings.py                    # Configurações
│   └── urls.py                        # Rotas principais
├── manage.py
└── requirements.txt
```

## 🗄️ Modelos do Sistema

### Professor
- **Dados Pessoais:**
  - Nome completo
  - CPF (único, com validação)
  - Telefone
  - Email

- **Dados Profissionais:**
  - Matrícula (opcional, único)
  - Área de Atuação (25 opções disponíveis)
  - Escola de Lotação

- **Endereço:**
  - Logradouro e número
  - CEP (com busca automática)
  - Bairro
  - Cidade e Estado

### Escola
- Nome
- Código INEP (opcional, único)
- Endereço completo
- Telefone e email

### Bairro
- Nome (único)
- Cidade e Estado

## 🎨 Interface

### Dashboard
- **Cards coloridos** com estatísticas:
  - Total de professores
  - Professores com escola definida
  - Professores com área de atuação
  - Total de escolas cadastradas
- **Tabela** com últimos professores cadastrados
- **Gráficos** de:
  - Top 5 áreas de atuação
  - Top 5 escolas com mais professores
- **Botões de ação rápida**

### Lista de Professores
- Tabela responsiva e moderna
- **Filtros múltiplos:**
  - Busca geral
  - Por escola
  - Por área de atuação
- **Ações por professor:**
  - Ver detalhes completos
  - Editar informações
  - Excluir (com confirmação)
- **Estatísticas rápidas** da listagem

### Cadastro/Edição
- Formulário organizado em seções
- **Busca automática de CEP** via ViaCEP
- **Modais AJAX** para cadastrar:
  - Nova escola (sem sair da página)
  - Novo bairro (sem sair da página)
- Validações em tempo real
- Máscaras de input (CPF, CEP, telefone)

### Detalhes do Professor
- Visualização completa e organizada
- Cards separados por categoria:
  - Informações pessoais
  - Informações profissionais
  - Endereço completo
- Botões de ação diretos

## 🔐 Sistema de Autenticação

- Login obrigatório em todas as páginas (exceto login)
- Logout seguro
- Mensagens de feedback visuais
- Redirecionamento automático após login
- Proteção de rotas com `@login_required`

## 📱 Responsividade

- **100% responsivo** - funciona em:
  - Desktop (1920px+)
  - Tablet (768px - 1024px)
  - Mobile (< 768px)
- Bootstrap 5.3
- Bootstrap Icons 1.11
- Tabelas responsivas com scroll horizontal em mobile

## 🎨 Customização de Cores

As cores principais podem ser alteradas no `base.html`:

```css
:root {
    --primary-color: #2c3e50;    /* Azul escuro */
    --secondary-color: #3498db;   /* Azul claro */
    --success-color: #27ae60;     /* Verde */
    --warning-color: #f39c12;     /* Laranja */
    --danger-color: #e74c3c;      /* Vermelho */
    --light-bg: #ecf0f1;          /* Cinza claro */
}
```

## 🔍 Áreas de Atuação Disponíveis

O sistema oferece 25 áreas de atuação:
- Língua Portuguesa, Matemática, História, Geografia
- Ciências, Física, Química, Biologia
- Educação Física, Arte
- Língua Estrangeira (Inglês e Espanhol)
- Ensino Religioso, Filosofia, Sociologia
- Literatura, Redação
- Educação Infantil
- Anos Iniciais e Finais do Ensino Fundamental
- Ensino Médio
- Gestão Escolar, Coordenação Pedagógica
- Biblioteconomia, Psicologia Escolar
- Outras

## 🔄 Próximas Implementações Sugeridas

### Relatórios
- [ ] Relatório de professores por escola
- [ ] Relatório de professores por área
- [ ] Relatório de professores por cidade
- [ ] Exportação para PDF
- [ ] Exportação para Excel

### Funcionalidades Extras
- [ ] Importação em lote (CSV/Excel)
- [ ] Foto do professor
- [ ] Histórico de alterações
- [ ] Anexar documentos (diplomas, certificados)
- [ ] Sistema de permissões diferenciadas
- [ ] Envio de email para professores
- [ ] Dashboard com gráficos interativos (Chart.js)
- [ ] API REST para integração
- [ ] Backup automático do banco de dados

## 🐛 Correções Aplicadas

✅ **Removido** todo código relacionado a Ordens de Serviço
✅ **Simplificado** o sistema para focar apenas em gestão de professores
✅ **Encoding UTF-8** corrigido em todos os templates
✅ **Interface moderna** com gradientes e animações
✅ **Sistema de mensagens** visual com ícones
✅ **Filtros funcionais** na listagem
✅ **Validações** de CPF e formulários
✅ **Responsividade** total

## 🎯 Casos de Uso

1. **Cadastrar Professor:**
   - Acesse "Professores" > "Novo Professor"
   - Preencha os dados pessoais e profissionais
   - Use o botão de busca de CEP para preencher endereço automaticamente
   - Crie escola/bairro diretamente se não existirem
   - Salve o cadastro

2. **Buscar Professor:**
   - Acesse "Professores" > "Listar Professores"
   - Use os filtros: busca geral, escola ou área
   - Clique em "Ver detalhes" para informações completas

3. **Editar Professor:**
   - Na lista ou detalhes, clique em "Editar"
   - Modifique os dados necessários
   - Salve as alterações

4. **Excluir Professor:**
   - Clique em "Excluir" (ícone de lixeira)
   - Confirme a exclusão
   - O professor será removido permanentemente

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato através do sistema de issues do projeto.

## 📝 Licença

Este projeto é de uso interno educacional.

---

**Desenvolvido com ❤️ usando Django 5.2 e Bootstrap 5.3**

#   s i s p r o f _ p r o j e c t  
 
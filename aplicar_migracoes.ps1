# Script para aplicar migrações no projeto Sisprof
Write-Host "=== Aplicando Migrações do Projeto Sisprof ===" -ForegroundColor Cyan
Write-Host ""

# Navega para o diretório do projeto
Set-Location "C:\Users\JB\sisprof_project"

Write-Host "1. Verificando ambiente virtual..." -ForegroundColor Yellow

# Verifica se o ambiente virtual existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "   Ambiente virtual encontrado!" -ForegroundColor Green
    
    Write-Host "2. Ativando ambiente virtual..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Host "3. Verificando instalação do Django..." -ForegroundColor Yellow
    $djangoCheck = python -c "import django; print(django.get_version())" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Django encontrado: $djangoCheck" -ForegroundColor Green
        
        Write-Host "4. Aplicando migrações..." -ForegroundColor Yellow
        python manage.py migrate
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=== Migrações aplicadas com sucesso! ===" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "=== Erro ao aplicar migrações ===" -ForegroundColor Red
        }
    } else {
        Write-Host "   Django não encontrado. Instalando dependências..." -ForegroundColor Yellow
        Write-Host "4. Instalando dependências do requirements.txt..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host "5. Aplicando migrações..." -ForegroundColor Yellow
        python manage.py migrate
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=== Migrações aplicadas com sucesso! ===" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "=== Erro ao aplicar migrações ===" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Você pode:" -ForegroundColor Yellow
    Write-Host "1. Criar um ambiente virtual: python -m venv venv" -ForegroundColor White
    Write-Host "2. Ou executar manualmente os comandos:" -ForegroundColor White
    Write-Host "   - Ativar o venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   - Instalar dependências: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "   - Aplicar migrações: python manage.py migrate" -ForegroundColor White
}

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


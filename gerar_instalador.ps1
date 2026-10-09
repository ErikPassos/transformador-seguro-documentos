$ErrorActionPreference = "Stop"

Write-Host "=== Transformador Seguro - Build Windows ===" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$RequiredFiles = @(
    "interface.py",
    "processamento.py",
    "validacao.py",
    "inspecao.py",
    "deteccao_tabelas.py",
    "extracao_tabelas.py",
    "exportacao_excel.py",
    "TransformadorSeguro.spec",
    "instalador.iss"
)

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path $File)) {
        throw "Arquivo obrigatorio ausente: $File"
    }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    py -m venv .venv
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-desktop.txt

Write-Host "Validando sintaxe..." -ForegroundColor Yellow
$PythonFiles = @(
    "interface.py",
    "processamento.py",
    "validacao.py",
    "inspecao.py",
    "deteccao_tabelas.py",
    "extracao_tabelas.py",
    "exportacao_excel.py"
)
foreach ($File in $PythonFiles) {
    & $Python -m py_compile $File
}

Write-Host "Gerando aplicativo com PyInstaller..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force TransformadorSeguro.spec.bak -ErrorAction SilentlyContinue
& $Python -m PyInstaller --noconfirm --clean TransformadorSeguro.spec

$AppExe = Join-Path $ProjectRoot "dist\TransformadorSeguro\TransformadorSeguro.exe"
if (-not (Test-Path $AppExe)) {
    throw "PyInstaller nao criou o executavel esperado: $AppExe"
}

$PossibleCompilers = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
)

$Iscc = $PossibleCompilers | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) {
    throw "Inno Setup 6 nao encontrado. Instale-o e execute este script novamente."
}

Write-Host "Gerando instalador com Inno Setup..." -ForegroundColor Yellow
& $Iscc "instalador.iss"

$SetupExe = Join-Path $ProjectRoot "instalador\TransformadorSeguro-Setup-1.0.0.exe"
if (-not (Test-Path $SetupExe)) {
    throw "Instalador nao foi criado no caminho esperado: $SetupExe"
}

Write-Host "" 
Write-Host "Build concluido com sucesso." -ForegroundColor Green
Write-Host "Aplicativo: $AppExe"
Write-Host "Instalador: $SetupExe"

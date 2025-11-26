# 🚀 AI Chat Assistant - PowerShell Launcher
# Продвинутый запуск с фоновым режимом

param(
    [switch]$Background,
    [switch]$Menu,
    [switch]$Test,
    [switch]$Clean
)

$script:AppDir = Split-Path -Parent $MyInvocation.MyCommandPath
$script:ServerPort = 5000
$script:ServerUrl = "http://localhost:$script:ServerPort"

function Write-Header {
    Write-Host "`n" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "🚀 AI CHAT ASSISTANT - POWERSHELL LAUNCHER" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
}

function Check-Python {
    Write-Host "🔍 Проверка Python..." -ForegroundColor Cyan
    
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        Write-Host "❌ Python не найден! Пожалуйста установите Python с https://python.org" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ Python найден: $($python.Source)" -ForegroundColor Green
    return $true
}

function Check-Dependencies {
    Write-Host "`n🔍 Проверка зависимостей..." -ForegroundColor Cyan
    
    try {
        $output = python -c "import flask, flask_cors; print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Зависимости установлены" -ForegroundColor Green
            return $true
        }
    } catch {}
    
    Write-Host "❌ Зависимости отсутствуют" -ForegroundColor Yellow
    Write-Host "📦 Установка Flask и Flask-CORS..." -ForegroundColor Yellow
    
    $reqFile = Join-Path $script:AppDir "requirements.txt"
    if (Test-Path $reqFile) {
        python -m pip install -r $reqFile -q
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Зависимости установлены" -ForegroundColor Green
            return $true
        }
    }
    
    Write-Host "❌ Ошибка при установке зависимостей" -ForegroundColor Red
    return $false
}

function Check-Files {
    Write-Host "`n🔍 Проверка файлов приложения..." -ForegroundColor Cyan
    
    $files = @("index.html", "styles.css", "auth.js", "script.js", "server.py")
    $allFound = $true
    
    foreach ($file in $files) {
        $path = Join-Path $script:AppDir $file
        if (Test-Path $path) {
            Write-Host "  ✅ $file" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file - НЕ НАЙДЕН" -ForegroundColor Red
            $allFound = $false
        }
    }
    
    return $allFound
}

function Start-Server {
    Write-Host "`n🚀 Запуск Flask сервера..." -ForegroundColor Green
    Write-Host "   URL: $script:ServerUrl" -ForegroundColor Cyan
    Write-Host "   Нажмите Ctrl+C для остановки`n" -ForegroundColor Cyan
    
    Push-Location $script:AppDir
    python server.py
    Pop-Location
}

function Start-ServerBackground {
    Write-Host "`n🚀 Запуск Flask сервера в фоне..." -ForegroundColor Green
    
    $job = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        python server.py
    } -ArgumentList $script:AppDir -Name "AIServer"
    
    Write-Host "✅ Сервер запущен (Job ID: $($job.Id))" -ForegroundColor Green
    
    # Подождать, пока сервер готов
    Write-Host "⏱️  Ожидание готовности сервера..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    
    # Проверить готовность
    $ready = $false
    for ($i = 0; $i -lt 10; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$script:ServerUrl/api/health" -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $ready = $true
                break
            }
        } catch {}
        Start-Sleep -Seconds 1
    }
    
    if ($ready) {
        Write-Host "✅ Сервер готов!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Сервер может быть не полностью готов" -ForegroundColor Yellow
    }
    
    return $job.Id
}

function Open-Browser {
    Write-Host "`n🌐 Открытие браузера..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    Start-Process $script:ServerUrl
    Write-Host "✅ Браузер открыт на $script:ServerUrl" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "`n🧪 Запуск тестирования API..." -ForegroundColor Cyan
    Push-Location $script:AppDir
    python test_api.py
    Pop-Location
}

function Show-Menu {
    while ($true) {
        Write-Host "`n" -ForegroundColor Green
        Write-Host "📋 МЕНЮ ЗАПУСКА:" -ForegroundColor Green
        Write-Host "   1. 🚀 Запустить сервер" -ForegroundColor Yellow
        Write-Host "   2. 🚀 Запустить сервер в фоне + открыть браузер" -ForegroundColor Yellow
        Write-Host "   3. 🧪 Запустить тестирование API" -ForegroundColor Yellow
        Write-Host "   4. 📊 Показать статус сервера" -ForegroundColor Yellow
        Write-Host "   5. 🛑 Остановить все сервера" -ForegroundColor Yellow
        Write-Host "   6. ❌ Выход" -ForegroundColor Yellow
        Write-Host ""
        
        $choice = Read-Host "Выберите действие (1-6)"
        
        switch ($choice) {
            "1" { Start-Server }
            "2" {
                $jobId = Start-ServerBackground
                Open-Browser
                Write-Host "`nСервер работает в фоне (Job ID: $jobId)" -ForegroundColor Cyan
                Write-Host "Наберите 'Get-Job -Id $jobId | Receive-Job' чтобы увидеть логи" -ForegroundColor Cyan
                Read-Host "Нажмите Enter для возврата в меню"
            }
            "3" { Run-Tests }
            "4" {
                Write-Host "`n📊 Статус сервера:" -ForegroundColor Cyan
                $jobs = Get-Job -Name "AIServer" -ErrorAction SilentlyContinue
                if ($jobs) {
                    foreach ($job in $jobs) {
                        Write-Host "  Job ID: $($job.Id), Статус: $($job.State)" -ForegroundColor Green
                    }
                } else {
                    Write-Host "  Сервер не запущен в фоне" -ForegroundColor Yellow
                }
            }
            "5" {
                Write-Host "`n🛑 Остановка всех серверов..." -ForegroundColor Yellow
                Get-Job -Name "AIServer" -ErrorAction SilentlyContinue | Stop-Job | Remove-Job
                Write-Host "✅ Все серверы остановлены" -ForegroundColor Green
            }
            "6" {
                Write-Host "`n👋 До свидания!`n" -ForegroundColor Green
                exit 0
            }
            default {
                Write-Host "❌ Неверный выбор" -ForegroundColor Red
            }
        }
    }
}

function Cleanup-App {
    Write-Host "`n🧹 Очистка данных приложения..." -ForegroundColor Cyan
    
    $dataDir = Join-Path $script:AppDir "data"
    if (Test-Path $dataDir) {
        Remove-Item $dataDir -Recurse -Force
        Write-Host "✅ Папка 'data' удалена" -ForegroundColor Green
    }
}

# Main
Write-Header

# Проверки
if (-not (Check-Python)) { exit 1 }
if (-not (Check-Dependencies)) { exit 1 }
if (-not (Check-Files)) { exit 1 }

# Выбрать действие
if ($Clean) {
    Cleanup-App
    Write-Host "`n✅ Очистка завершена" -ForegroundColor Green
} elseif ($Background) {
    Write-Host ""
    $jobId = Start-ServerBackground
    Open-Browser
} elseif ($Test) {
    Write-Host ""
    Run-Tests
} else {
    Write-Host ""
    Show-Menu
}

Write-Host ""

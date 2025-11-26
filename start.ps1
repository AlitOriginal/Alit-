# AI Chat Server Manager - PowerShell Version
param(
    [string]$action = ""
)

function Show-Menu {
    Clear-Host
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "   🚀 AI CHAT ASSISTANT - УПРАВЛЕНИЕ СЕРВЕРОМ" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Выбор действия:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   1. 🚀 Запустить менеджер сервера"
    Write-Host "   2. ⚙️  Установить зависимости"
    Write-Host "   3. 🌐 Открыть приложение в браузере"
    Write-Host "   4. 📁 Открыть папку проекта"
    Write-Host "   5. 📖 Показать README"
    Write-Host "   6. ❌ Выход"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "📦 Установка зависимостей..." -ForegroundColor Yellow
    Write-Host ""
    
    $pythonCheck = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python не установлен или не доступен в PATH!" -ForegroundColor Red
        Write-Host "Пожалуйста установите Python с https://www.python.org/" -ForegroundColor Yellow
        return
    }
    
    Write-Host "✅ Python найден: $pythonCheck" -ForegroundColor Green
    Write-Host ""
    
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Зависимости успешно установлены!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Ошибка при установке зависимостей" -ForegroundColor Red
    }
    
    Read-Host "Нажмите Enter для продолжения"
}

function Start-Manager {
    Write-Host "🚀 Запуск менеджера сервера..." -ForegroundColor Yellow
    Write-Host ""
    python manage_server.py
}

function Open-Browser {
    Write-Host "🌐 Открытие приложения в браузере..." -ForegroundColor Yellow
    $browserPath = "index.html"
    $fullPath = (Get-Item -Path ".").FullName + "\$browserPath"
    
    if (Test-Path $fullPath) {
        Start-Process $fullPath
        Write-Host "✅ Приложение открыто в браузере!" -ForegroundColor Green
    } else {
        Write-Host "❌ Файл index.html не найден!" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

function Open-Folder {
    Write-Host "📁 Открытие папки проекта..." -ForegroundColor Yellow
    Invoke-Item "."
}

function Show-Readme {
    if (Test-Path "README.md") {
        Write-Host ""
        Get-Content README.md
        Write-Host ""
    } else {
        Write-Host "❌ README.md не найден!" -ForegroundColor Red
    }
    
    Read-Host "Нажмите Enter для продолжения"
}

function Main {
    do {
        Show-Menu
        
        if ($action -eq "") {
            $choice = Read-Host "Введите номер (1-6)"
        } else {
            $choice = $action
            $action = ""
        }
        
        switch ($choice) {
            "1" {
                Start-Manager
            }
            "2" {
                Install-Dependencies
            }
            "3" {
                Open-Browser
            }
            "4" {
                Open-Folder
            }
            "5" {
                Show-Readme
            }
            "6" {
                Write-Host ""
                Write-Host "👋 До свидания!" -ForegroundColor Green
                exit
            }
            default {
                Write-Host ""
                Write-Host "❌ Неверный выбор! Пожалуйста выберите 1-6" -ForegroundColor Red
                Start-Sleep -Seconds 2
            }
        }
    } while ($true)
}

Main

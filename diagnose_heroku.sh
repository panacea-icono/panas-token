#!/bin/bash

# Script de diagnóstico para problemas de Heroku
# Uso: ./diagnose_heroku.sh

echo "=== Diagnóstico de Heroku ==="

echo "🔍 Verificando autenticación..."
heroku auth:whoami
echo ""

echo "🔍 Verificando configuración de organización..."
heroku config --help | grep -A 5 -B 5 "organization" || echo "No se encontró información de organización"
echo ""

echo "🔍 Verificando teams/organizaciones..."
heroku teams || echo "No se pudieron listar teams"
echo ""

echo "🔍 Verificando información de cuenta..."
heroku account || echo "No se pudo obtener información de cuenta"
echo ""

echo "🔍 Verificando versión de Heroku CLI..."
heroku --version
echo ""

echo "🔍 Verificando si hay configuración local que cause conflictos..."
if [ -f ~/.netrc ]; then
    echo "Archivo .netrc encontrado:"
    grep heroku ~/.netrc || echo "No hay entradas de Heroku en .netrc"
else
    echo "No se encontró archivo .netrc"
fi
echo ""

echo "🔍 Verificando variables de entorno de Heroku..."
env | grep HEROKU || echo "No hay variables de entorno de Heroku"
echo ""

echo "=== Posibles soluciones ==="
echo ""
echo "1. Si el error persiste, intenta cerrar sesión y volver a autenticarte:"
echo "   heroku auth:logout"
echo "   heroku auth:login"
echo ""
echo "2. Si estás en una organización/team, verifica que tengas permisos:"
echo "   heroku teams"
echo "   heroku members -t [team-name]"
echo ""
echo "3. Si el problema persiste, intenta crear la app desde el dashboard web:"
echo "   https://dashboard.heroku.com/new-app"
echo ""
echo "4. Una vez creada la app desde el web, conecta el repositorio:"
echo "   heroku git:remote -a [nombre-de-tu-app]"

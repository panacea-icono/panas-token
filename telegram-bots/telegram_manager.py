#!/usr/bin/env python3
"""
Telegram Bot Manager para PANAS Token
Gestiona múltiples bots de Telegram con diferentes funcionalidades
Integración completa con NFDomains de Algorand
"""

import os
import asyncio
import lo**👨‍⚕️ Asistentes Médicos (ChatGPT):**
- `/consulta` - Consulta médica general
- `/vaser` - Consulta Clínica Vaser
- `/medico` - Asistente médico especializado
- `/cita` - Agendar cita con Liliana
- `/asistentes` - Ver todos los asistentes

**🏥 Panacea API Central:**
- `/panacea` - Estado de integración
- `/sync` - Sincronizar datos con Panacea
- `/activos` - Ver activos médicos tokenizados
- `/historial` - Consultar historial médico

**🔬 Investigación Médica:**
- `/studies` - Estudios disponibles
- `/participate` - Unirse a estudio
- `/rewards` - Ver recompensas ganadastelegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import redis.asyncio as redis
from typing import Dict, List, Optional
import json
from loguru import logger

# Importar integración NFDomains
from nfd_integration import nfd_api, nfd_telegram, cleanup_nfd_resources
from panas_nfd_domains import panas_nfd

# Importar integración médica
import sys
sys.path.append('/app/../ai-models/chatgpt-medical')
from medical_gpt_integration import medical_gpt

# Importar integración Panacea API Central
sys.path.append('/app/../panacea-central')
from panacea_integration import panacea_integration

# Configuración
PANAS_API_URL = os.getenv("PANAS_API_URL", "http://localhost:8000")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BOLIVIACHIC_WEBSITE = "https://boliviachic.com"
PANACEA_API_URL = os.getenv("PANACEA_API_URL", "http://panacea-api-central:8000")

# Tokens de los bots con nombres descriptivos
BOT_TOKENS = {
    "panas_main": "8187502572:AAFn2bEOOqDipeDWTnszjyWyiBUUBsofMis",      # Bot principal PANAS
    "ai_assistant": "7155901429:AAFTyNZ2VQlufM8gR-TQCiMPD1rsE1qqOAE",    # Bot asistente de IA
    "code_helper": "7622504424:AAGQjIbXs3fs9ITUiDFBuzNG5PmJHb4Sxao",     # Bot ayudante de código
    "tokenizado_bot": "7985123456:AAFk3mEOOqDipeDWTnszjyWyiBUUBsofXyz",  # Bot para tokenizado.algo
    "panacea_bot": "7985654321:AAGp4nEOOqDipeDWTnszjyWyiBUUBsofAbc",     # Bot para panacea.icono.algo
    "activo_bot": "7985987654:AAHq5oEOOqDipeDWTnszjyWyiBUUBsofDef"       # Bot para activo.algo
}

class PanasTelegramBot:
    def __init__(self, token: str, bot_name: str):
        self.token = token
        self.bot_name = bot_name
        self.application = Application.builder().token(token).build()
        self.redis_client = None

    async def setup_redis(self):
        """Configurar conexión Redis"""
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()
            logger.info(f"Redis conectado para bot {self.bot_name}")
        except Exception as e:
            logger.error(f"Error conectando Redis: {e}")

    async def call_panas_api(self, endpoint: str, data: dict = None) -> dict:
        """Llamar a la API de PANAS"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{PANAS_API_URL}{endpoint}"
                if data:
                    async with session.post(url, json=data) as response:
                        return await response.json()
                else:
                    async with session.get(url) as response:
                        return await response.json()
        except Exception as e:
            logger.error(f"Error llamando API PANAS: {e}")
            return {"error": str(e)}

    async def call_ollama_api(self, prompt: str, model: str = "llama2") -> str:
        """Llamar a Ollama para IA local"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                async with session.post(f"{OLLAMA_API_URL}/api/generate", json=data) as response:
                    result = await response.json()
                    return result.get("response", "Error en respuesta")
        except Exception as e:
            logger.error(f"Error llamando Ollama: {e}")
            return f"Error conectando con IA: {e}"

class PanasMainBot(PanasTelegramBot):
    """Bot principal para gestión de tokens PANAS"""

    def __init__(self, token: str):
        super().__init__(token, "panas_main")
        self.setup_handlers()

    def setup_handlers(self):
        """Configurar comandos del bot principal"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("transfer", self.transfer_command))
        self.application.add_handler(CommandHandler("price", self.price_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Comandos NFDomains
        self.application.add_handler(CommandHandler("domains", self.domains_command))
        self.application.add_handler(CommandHandler("domain", self.domain_command))
        self.application.add_handler(CommandHandler("nfd", self.nfd_info_command))
        self.application.add_handler(CommandHandler("website", self.website_command))

        # Comandos médicos (integración ChatGPT)
        self.application.add_handler(CommandHandler("consulta", self.medical_consultation_command))
        self.application.add_handler(CommandHandler("vaser", self.vaser_consultation_command))
        self.application.add_handler(CommandHandler("medico", self.medical_assistant_command))
        self.application.add_handler(CommandHandler("cita", self.appointment_command))
        self.application.add_handler(CommandHandler("asistentes", self.list_medical_assistants_command))
        
        # Comandos Panacea API Central
        self.application.add_handler(CommandHandler("panacea", self.panacea_status_command))
        self.application.add_handler(CommandHandler("sync", self.sync_user_data_command))
        self.application.add_handler(CommandHandler("activos", self.medical_assets_command))
        self.application.add_handler(CommandHandler("historial", self.medical_history_command))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_msg = """
🎯 **Bienvenido a PANAS Token Bot!**

PANAS es un token especializado en investigación médica y recompensas por participación en estudios científicos.

**Comandos disponibles:**
- `/balance` - Ver tu balance de tokens
- `/transfer` - Transferir tokens
- `/price` - Precio actual del token
- `/help` - Ayuda detallada

🔬 **Sobre PANAS:**
Nuestros tokens recompensan la participación en investigación médica, facilitando el avance científico mientras los usuarios ganan por contribuir.
        """
        await update.message.reply_text(welcome_msg)

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /balance"""
        user_id = update.effective_user.id

        # Llamar a la API para obtener balance
        result = await self.call_panas_api(f"/users/{user_id}/balance")

        if "error" in result:
            await update.message.reply_text("❌ Error obteniendo balance. Intenta más tarde.")
        else:
            balance = result.get("balance", "0")
            await update.message.reply_text(f"💰 Tu balance: **{balance} PANAS**")

    async def transfer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /transfer"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso: `/transfer <destinatario> <cantidad>`\n"
                "Ejemplo: `/transfer @usuario 100`"
            )
            return

        recipient = context.args[0]
        try:
            amount = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Cantidad inválida")
            return

        # Simular transferencia
        await update.message.reply_text(
            f"✅ Transferencia iniciada:\n"
            f"🎯 Para: {recipient}\n"
            f"💰 Cantidad: {amount} PANAS\n"
            f"⏳ Procesando..."
        )

    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /price"""
        result = await self.call_panas_api("/token/price")

        if "error" in result:
            await update.message.reply_text("❌ Error obteniendo precio")
        else:
            price = result.get("price_usd", "0.00")
            change = result.get("change_24h", "0.00")
            await update.message.reply_text(
                f"📊 **Precio PANAS**\n"
                f"💵 Precio: ${price}\n"
                f"📈 Cambio 24h: {change}%"
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = """
🔗 **PANAS Token - Ayuda Completa**

**🎯 ¿Qué es PANAS?**
Token para investigación médica que recompensa la participación en estudios científicos.

**💰 Comandos de Tokens:**
- `/balance` - Ver balance actual
- `/transfer <usuario> <cantidad>` - Transferir tokens
- `/price` - Precio y estadísticas

**🌐 Dominios NFD Algorand:**
- `/domains` - Ver todos los dominios PANAS
- `/domain <nombre>` - Info específica de dominio
- `/nfd` - Información sobre NFDomains
- `/website` - Acceder al sitio web principal

**�‍⚕️ Asistentes Médicos (ChatGPT):**
- `/consulta` - Consulta médica general
- `/vaser` - Consulta Clínica Vaser
- `/medico` - Asistente médico especializado
- `/cita` - Agendar cita con Liliana
- `/asistentes` - Ver todos los asistentes

**�🔬 Investigación Médica:**
- `/studies` - Estudios disponibles
- `/participate` - Unirse a estudio
- `/rewards` - Ver recompensas ganadas

**📞 Soporte:**
- `/contact` - Contactar soporte
- `/status` - Estado del sistema

🌍 **Web:** https://boliviachic.com
Desarrollado con ❤️ para el avance científico
        """
        await update.message.reply_text(help_text)

    async def domains_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /domains - Mostrar todos los dominios PANAS"""
        try:
            await update.message.reply_text("🌐 Obteniendo información de dominios PANAS...")

            async with panas_nfd as manager:
                all_domains = await manager.get_all_domains_status()

                message = "🌐 **Dominios NFD de PANAS Token**\n\n"

                for domain_name, domain_info in all_domains["domains"].items():
                    config = domain_info["config"]
                    status_emoji = "✅" if domain_info.get("status") == "active" else "❓"

                    message += f"{status_emoji} **{domain_name}**\n"
                    message += f"   {config['description']}\n"
                    message += f"   Tipo: {config['type'].title()}\n\n"

                message += f"📊 **Total:** {all_domains['total_domains']} dominios\n"
                message += f"🌍 **Web:** {all_domains['website']}\n"
                message += f"🔗 **Registry:** {all_domains['nfd_registry']}\n\n"
                message += "💡 Usa `/domain <nombre>` para información detallada"

            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"Error en comando domains: {e}")
            await update.message.reply_text("❌ Error obteniendo información de dominios")

    async def domain_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /domain <nombre> - Información específica de dominio"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: `/domain <nombre>`\n\n"
                "**Dominios disponibles:**\n"
                "• `10.panas.algo` - Dominio principal\n"
                "• `tokenizado.algo` - Tokenización\n"
                "• `panacea.icono.algo` - Servicios médicos\n"
                "• `activo.algo` - Gestión de activos"
            )
            return

        domain_name = context.args[0]

        try:
            async with panas_nfd as manager:
                message = manager.get_domain_telegram_info(domain_name)

            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"Error en comando domain: {e}")
            await update.message.reply_text(f"❌ Error obteniendo información del dominio {domain_name}")

    async def nfd_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /nfd - Información sobre NFDomains"""
        nfd_info = """
🌐 **NFDomains - Algorand Name Service**

**¿Qué son los NFDomains?**
Los NFDomains son dominios descentralizados en la blockchain de Algorand que funcionan como NFTs.

**Dominios PANAS registrados:**
🔹 `10.panas.algo` - Dominio principal
🔹 `tokenizado.algo` - Servicios de tokenización
🔹 `panacea.icono.algo` - Marca visual Panacea
🔹 `activo.algo` - Gestión de activos digitales

**Características:**
✅ Propiedad verificable en blockchain
✅ Resolución a direcciones Algorand
✅ Metadatos personalizables
✅ Transferibles como NFTs

🔗 **Enlaces útiles:**
• NFDomains App: https://app.nf.domains
• Documentación: https://docs.nf.domains
• Sitio Web PANAS: https://boliviachic.com

💡 Usa `/domains` para ver el estado actual de todos los dominios
        """
        await update.message.reply_text(nfd_info, parse_mode='Markdown')

    async def website_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /website - Acceso al sitio web"""
        website_msg = """
🌍 **Sitio Web PANAS Token**

🔗 **URL Principal:** https://boliviachic.com

**Acceso directo a servicios:**
🌐 NFDomains:
• https://app.nf.domains/name/10.panas.algo
• https://app.nf.domains/name/tokenizado.algo
• https://app.nf.domains/name/panacea.icono.algo
• https://app.nf.domains/name/activo.algo

**¿Qué encontrarás en el sitio?**
📊 Panel de control de tokens
🔬 Estudios médicos disponibles
💰 Gestión de recompensas
📈 Estadísticas en tiempo real
🔐 Wallet integrado

¡Visita nuestro sitio para acceder a todas las funcionalidades!
        """
        await update.message.reply_text(website_msg, parse_mode='Markdown')

    # ====== COMANDOS MÉDICOS ======

    async def medical_consultation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /consulta - Consulta médica general"""
        if not context.args:
            await update.message.reply_text(
                "❤️ **Consulta Médica**\n\n"
                "Uso: `/consulta <tu pregunta médica>`\n\n"
                "Ejemplo: `/consulta ¿Qué cuidados necesito después de una liposucción?`\n\n"
                "**Asistentes disponibles:**\n"
                "• Clínica Vaser - Procedimientos estéticos\n"
                "• Asistente Médico - Seguimiento médico\n"
                "• Liliana GPT - Coordinación y atención"
            )
            return

        query = " ".join(context.args)
        user_id = update.effective_user.id

        await update.message.reply_text("🔍 Consultando con nuestros asistentes médicos...")

        try:
            # Obtener información del usuario para contexto
            context_data = await self._get_user_medical_context(user_id)

            # Enrutar automáticamente la consulta
            response = await medical_gpt.route_medical_query(query, context_data)

            if response["success"]:
                reply_msg = f"👨‍⚕️ **{response['assistant']}**\n"
                reply_msg += f"*Especialidad: {response['specialty']}*\n\n"
                reply_msg += response["response"]

                # Agregar información adicional si está disponible
                if "nfd_domain" in context_data:
                    reply_msg += f"\n\n🌐 Dominio NFD: {context_data['nfd_domain']}"

            else:
                reply_msg = f"❌ Error en consulta: {response.get('error', 'Error desconocido')}"

            await update.message.reply_text(reply_msg)

        except Exception as e:
            logger.error(f"Error en consulta médica: {e}")
            await update.message.reply_text("❌ Error procesando consulta. Intenta más tarde.")

    async def vaser_consultation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /vaser - Consulta específica sobre procedimientos Vaser"""
        if not context.args:
            await update.message.reply_text(
                "🏥 **Consulta Clínica Vaser**\n\n"
                "Uso: `/vaser <tu pregunta sobre procedimientos Vaser>`\n\n"
                "Ejemplos:\n"
                "• `/vaser ¿Cuánto cuesta una liposucción Vaser?`\n"
                "• `/vaser ¿Soy candidato para Vaser?`\n"
                "• `/vaser Cuidados postoperatorios`"
            )
            return

        query = " ".join(context.args)
        user_id = update.effective_user.id

        await update.message.reply_text("🏥 Consultando con el especialista en Clínica Vaser...")

        try:
            context_data = await self._get_user_medical_context(user_id)

            # Consultar específicamente al asistente de Clínica Vaser
            response = await medical_gpt.get_assistant_response("clinica_vaser", query, context_data)

            if response["success"]:
                reply_msg = f"🏥 **Clínica Vaser - Especialista**\n\n"
                reply_msg += response["response"]
                reply_msg += "\n\n💡 *Para agendar una cita, usa `/cita`*"
            else:
                reply_msg = f"❌ Error en consulta Vaser: {response.get('error', 'Error desconocido')}"

            await update.message.reply_text(reply_msg)

        except Exception as e:
            logger.error(f"Error en consulta Vaser: {e}")
            await update.message.reply_text("❌ Error procesando consulta Vaser. Intenta más tarde.")

    async def medical_assistant_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /medico - Consulta con asistente médico"""
        if not context.args:
            await update.message.reply_text(
                "👨‍⚕️ **Asistente Médico**\n\n"
                "Uso: `/medico <consulta médica especializada>`\n\n"
                "Especializado en:\n"
                "• Evaluaciones preoperatorias\n"
                "• Seguimiento postoperatorio\n"
                "• Protocolos médicos\n"
                "• Manejo de complicaciones"
            )
            return

        query = " ".join(context.args)
        user_id = update.effective_user.id

        await update.message.reply_text("👨‍⚕️ Consultando con el asistente médico especializado...")

        try:
            context_data = await self._get_user_medical_context(user_id)

            # Consultar específicamente al asistente médico
            response = await medical_gpt.get_assistant_response("medico_vaser", query, context_data)

            if response["success"]:
                reply_msg = f"👨‍⚕️ **Asistente Médico Especializado**\n\n"
                reply_msg += response["response"]
            else:
                reply_msg = f"❌ Error en consulta médica: {response.get('error', 'Error desconocido')}"

            await update.message.reply_text(reply_msg)

        except Exception as e:
            logger.error(f"Error en consulta médica: {e}")
            await update.message.reply_text("❌ Error procesando consulta médica. Intenta más tarde.")

    async def appointment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /cita - Agendar cita con Liliana GPT"""
        if not context.args:
            await update.message.reply_text(
                "📅 **Agendar Cita**\n\n"
                "Uso: `/cita <detalles de la cita que deseas agendar>`\n\n"
                "Ejemplos:\n"
                "• `/cita Quiero agendar consulta para liposucción`\n"
                "• `/cita Necesito seguimiento postoperatorio`\n"
                "• `/cita Información sobre precios y financiamiento`"
            )
            return

        request = " ".join(context.args)
        user_id = update.effective_user.id

        await update.message.reply_text("📅 Coordinando tu cita con Liliana...")

        try:
            context_data = await self._get_user_medical_context(user_id)

            # Consultar específicamente a Liliana GPT para coordinación
            response = await medical_gpt.get_assistant_response("liliana_gpt", request, context_data)

            if response["success"]:
                reply_msg = f"📅 **Liliana - Coordinadora de Citas**\n\n"
                reply_msg += response["response"]
                reply_msg += "\n\n📞 *Te contactaremos pronto para confirmar los detalles*"
            else:
                reply_msg = f"❌ Error agendando cita: {response.get('error', 'Error desconocido')}"

            await update.message.reply_text(reply_msg)

        except Exception as e:
            logger.error(f"Error agendando cita: {e}")
            await update.message.reply_text("❌ Error procesando solicitud de cita. Intenta más tarde.")

    async def list_medical_assistants_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /asistentes - Listar asistentes médicos disponibles"""
        try:
            assistants_info = await medical_gpt.get_all_assistants_info()

            reply_msg = "👨‍⚕️ **Asistentes Médicos Disponibles**\n\n"

            for assistant in assistants_info["assistants"]:
                reply_msg += f"🔹 **{assistant['name']}**\n"
                reply_msg += f"   *{assistant['specialty']}*\n"
                reply_msg += f"   {assistant['description']}\n\n"
                reply_msg += "   **Capacidades:**\n"
                for capability in assistant['capabilities']:
                    reply_msg += f"   • {capability}\n"
                reply_msg += "\n"

            reply_msg += "**Comandos disponibles:**\n"
            reply_msg += "• `/consulta` - Consulta general (enrutamiento automático)\n"
            reply_msg += "• `/vaser` - Consulta específica Clínica Vaser\n"
            reply_msg += "• `/medico` - Consulta médica especializada\n"
            reply_msg += "• `/cita` - Agendar cita con Liliana\n"

            await update.message.reply_text(reply_msg)

        except Exception as e:
            logger.error(f"Error listando asistentes: {e}")
            await update.message.reply_text("❌ Error obteniendo información de asistentes.")

    # ====== COMANDOS PANACEA API CENTRAL ======
    
    async def panacea_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /panacea - Estado de integración con Panacea API Central"""
        await update.message.reply_text("🔄 Verificando estado de Panacea API Central...")
        
        try:
            async with panacea_integration as api:
                status = await api.get_integration_status()
                
                if status.get("panacea_api_status") == "healthy":
                    reply_msg = "✅ **Panacea API Central - Estado Activo**\n\n"
                    reply_msg += f"🌐 **Repositorio:** https://github.com/panacea-icono/panacea-api-central\n"
                    reply_msg += f"🔗 **Integración PANAS:** Activa\n"
                    reply_msg += f"🤖 **ChatGPT Médico:** Conectado\n"
                    reply_msg += f"🌐 **NFDomains:** Integrado\n\n"
                    reply_msg += "**Endpoints disponibles:**\n"
                    
                    for endpoint in status.get("available_endpoints", []):
                        reply_msg += f"• {endpoint}\n"
                        
                    reply_msg += f"\n⏰ **Última verificación:** {status.get('last_check')}"
                else:
                    reply_msg = f"❌ **Error en Panacea API Central**\n\n"
                    reply_msg += f"Error: {status.get('error', 'Desconocido')}\n"
                    reply_msg += f"🌐 **Repositorio:** https://github.com/panacea-icono/panacea-api-central"
                
            await update.message.reply_text(reply_msg, parse_mode='Markdown', disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error verificando estado Panacea: {e}")
            await update.message.reply_text("❌ Error verificando estado de Panacea API Central")
    
    async def sync_user_data_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /sync - Sincronizar datos del usuario con Panacea Central"""
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("🔄 Sincronizando tus datos con Panacea Central...")
        
        try:
            # Obtener datos PANAS del usuario
            panas_data = await self._get_user_panas_data(user_id)
            
            async with panacea_integration as api:
                result = await api.sync_user_data(user_id, panas_data)
                
                if result.get("success"):
                    reply_msg = "✅ **Sincronización Completada**\n\n"
                    reply_msg += f"👤 **Usuario:** {user_id}\n"
                    reply_msg += f"💰 **Balance PANAS:** {panas_data.get('balance', 0)}\n"
                    reply_msg += f"🌐 **Dominios NFD:** {len(panas_data.get('nfd_domains', []))}\n"
                    reply_msg += f"🏥 **Consultas médicas:** {len(panas_data.get('consultations', []))}\n"
                    reply_msg += f"📊 **Estado:** Sincronizado con Panacea Central"
                else:
                    reply_msg = f"❌ **Error en sincronización**\n\nDetalle: {result.get('error')}"
                
            await update.message.reply_text(reply_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error sincronizando usuario {user_id}: {e}")
            await update.message.reply_text("❌ Error durante la sincronización")
    
    async def medical_assets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /activos - Ver activos médicos tokenizados"""
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("🔍 Consultando tus activos médicos tokenizados...")
        
        try:
            async with panacea_integration as api:
                assets = await api.get_medical_assets(user_id)
                
                if assets.get("success") and assets.get("assets"):
                    reply_msg = "🏥 **Tus Activos Médicos Tokenizados**\n\n"
                    
                    for asset in assets["assets"]:
                        reply_msg += f"🪙 **{asset.get('name', 'Asset')}**\n"
                        reply_msg += f"   Tipo: {asset.get('type', 'N/A')}\n"
                        reply_msg += f"   Valor: {asset.get('value', 0)} PANAS\n"
                        reply_msg += f"   Estado: {asset.get('status', 'N/A')}\n\n"
                    
                    reply_msg += f"📊 **Total de activos:** {len(assets['assets'])}\n"
                    reply_msg += "💡 *Los activos médicos representan tu participación en investigación*"
                
                elif assets.get("success") and not assets.get("assets"):
                    reply_msg = "📋 **No tienes activos médicos aún**\n\n"
                    reply_msg += "Para obtener activos médicos tokenizados:\n"
                    reply_msg += "• Participa en consultas médicas\n"
                    reply_msg += "• Completa estudios de investigación\n"
                    reply_msg += "• Usa `/consulta` para empezar"
                
                else:
                    reply_msg = f"❌ **Error consultando activos**\n\nDetalle: {assets.get('error')}"
                
            await update.message.reply_text(reply_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error consultando activos médicos: {e}")
            await update.message.reply_text("❌ Error consultando activos médicos")
    
    async def medical_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /historial - Ver historial médico en Panacea Central"""
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("📋 Consultando tu historial médico...")
        
        try:
            async with panacea_integration as api:
                # Obtener historial médico del usuario
                history_response = await api._make_request("GET", f"/medical/records?user_id={user_id}")
                
                if history_response.get("success") and history_response.get("records"):
                    reply_msg = "📋 **Tu Historial Médico**\n\n"
                    
                    for record in history_response["records"][-5:]:  # Últimos 5 registros
                        date = record.get("date", "N/A")
                        consultation_type = record.get("type", "General")
                        status = record.get("status", "Completada")
                        
                        reply_msg += f"📅 **{date}**\n"
                        reply_msg += f"   Tipo: {consultation_type}\n"
                        reply_msg += f"   Estado: {status}\n"
                        
                        if record.get("reward_panas"):
                            reply_msg += f"   Recompensa: {record['reward_panas']} PANAS\n"
                        
                        reply_msg += "\n"
                    
                    total_records = len(history_response["records"])
                    reply_msg += f"📊 **Total de registros:** {total_records}\n"
                    reply_msg += "💡 *Tus datos están seguros en Panacea Central*"
                
                elif history_response.get("success") and not history_response.get("records"):
                    reply_msg = "📋 **No tienes historial médico aún**\n\n"
                    reply_msg += "Para crear tu historial médico:\n"
                    reply_msg += "• Realiza consultas con `/consulta`\n"
                    reply_msg += "• Agenda citas con `/cita`\n"
                    reply_msg += "• Participa en estudios médicos"
                
                else:
                    reply_msg = f"❌ **Error consultando historial**\n\nDetalle: {history_response.get('error')}"
                
            await update.message.reply_text(reply_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error consultando historial médico: {e}")
            await update.message.reply_text("❌ Error consultando historial médico")
    
    async def _get_user_panas_data(self, user_id: str) -> Dict[str, Any]:
        """Obtener datos completos PANAS del usuario para sincronización"""
        panas_data = {"user_id": user_id, "nfd_domains": [], "consultations": []}
        
        try:
            # Obtener balance PANAS
            balance_result = await self.call_panas_api(f"/users/{user_id}/balance")
            if "balance" in balance_result:
                panas_data["balance"] = balance_result["balance"]
            
            # Obtener dominios NFD
            async with panas_nfd as manager:
                user_domains = []
                for domain_name in manager.domains.keys():
                    domain_info = await manager.get_domain_info(domain_name)
                    if domain_info.get("status") == "active":
                        user_domains.append({
                            "domain": domain_name,
                            "type": domain_info["config"]["type"],
                            "features": domain_info["config"]["features"]
                        })
                panas_data["nfd_domains"] = user_domains
            
            # Obtener historial de consultas del cache Redis
            if self.redis_client:
                consultation_key = f"user:{user_id}:consultations"
                consultations_data = await self.redis_client.get(consultation_key)
                if consultations_data:
                    panas_data["consultations"] = json.loads(consultations_data)
            
        except Exception as e:
            logger.warning(f"Error obteniendo datos PANAS para usuario {user_id}: {e}")
        
        return panas_data
    
    # ====== FIN COMANDOS PANACEA ======
````

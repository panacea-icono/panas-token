#!/usr/bin/env python3
"""
Integración con ChatGPT Medical Assistants para PANAS Token
Conecta con asistentes especializados en servicios médicos
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import json

@dataclass
class MedicalAssistant:
    """Configuración de asistente médico"""
    name: str
    gpt_id: str
    url: str
    specialty: str
    description: str
    capabilities: List[str]

# Configuración de asistentes médicos especializados
MEDICAL_ASSISTANTS = {
    "clinica_vaser": MedicalAssistant(
        name="Asistente Clínica Vaser",
        gpt_id="g-67ee9dacb42481918da137c4d26d321a",
        url="https://chatgpt.com/g/g-67ee9dacb42481918da137c4d26d321a-asistentes-clinica-vaser",
        specialty="Procedimientos estéticos y cirugía plástica",
        description="Especialista en tratamientos Vaser, liposucción y procedimientos estéticos",
        capabilities=[
            "Consultas sobre procedimientos Vaser",
            "Información sobre liposucción",
            "Cuidados pre y post operatorios",
            "Evaluación de candidatos",
            "Costos y financiamiento"
        ]
    ),
    "medico_vaser": MedicalAssistant(
        name="Asistente Médico Clínica Vaser",
        gpt_id="g-67ee9e5d4d3c819187086b7b8042adb2",
        url="https://chatgpt.com/g/g-67ee9e5d4d3c819187086b7b8042adb2-asistente-medico-clinica-vaser",
        specialty="Medicina estética y seguimiento médico",
        description="Asistente médico especializado en seguimiento y cuidados médicos",
        capabilities=[
            "Evaluación médica preoperatoria",
            "Seguimiento postoperatorio",
            "Manejo de complicaciones",
            "Protocolos médicos",
            "Historiales clínicos"
        ]
    ),
    "liliana_gpt": MedicalAssistant(
        name="Liliana GPT",
        gpt_id="g-68090d03cbd881919283ca54c3e57165",
        url="https://chatgpt.com/g/g-68090d03cbd881919283ca54c3e57165-liliana-gpt",
        specialty="Asistencia personalizada y coordinación",
        description="Asistente personal especializado en coordinación y atención al cliente",
        capabilities=[
            "Coordinación de citas",
            "Atención personalizada",
            "Seguimiento de pacientes",
            "Información general",
            "Soporte administrativo"
        ]
    )
}

class MedicalGPTIntegration:
    """Integración con asistentes médicos de ChatGPT"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.assistants = MEDICAL_ASSISTANTS

    async def get_assistant_response(
        self,
        assistant_type: str,
        user_message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Obtener respuesta de un asistente médico específico

        Args:
            assistant_type: Tipo de asistente (clinica_vaser, medico_vaser, liliana_gpt)
            user_message: Mensaje del usuario
            context: Contexto adicional (paciente, NFD, etc.)
        """
        if assistant_type not in self.assistants:
            raise ValueError(f"Asistente no encontrado: {assistant_type}")

        assistant = self.assistants[assistant_type]

        try:
            # Preparar el prompt con contexto
            enhanced_prompt = await self._enhance_prompt(user_message, assistant, context)

            # Llamada a la API de OpenAI
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": f"Eres {assistant.name}, especializado en {assistant.specialty}. {assistant.description}"
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "assistant": assistant.name,
                            "specialty": assistant.specialty,
                            "response": data["choices"][0]["message"]["content"],
                            "context": context,
                            "success": True
                        }
                    else:
                        error_data = await response.text()
                        logger.error(f"Error API OpenAI: {response.status} - {error_data}")
                        return {
                            "assistant": assistant.name,
                            "error": f"Error API: {response.status}",
                            "success": False
                        }

        except Exception as e:
            logger.error(f"Error en consulta a {assistant.name}: {e}")
            return {
                "assistant": assistant.name,
                "error": str(e),
                "success": False
            }

    async def _enhance_prompt(
        self,
        message: str,
        assistant: MedicalAssistant,
        context: Optional[Dict] = None
    ) -> str:
        """Mejorar el prompt con contexto específico"""
        enhanced = message

        if context:
            # Agregar información del paciente/usuario
            if "user_id" in context:
                enhanced += f"\n\nUsuario ID: {context['user_id']}"

            # Agregar información del dominio NFD
            if "nfd_domain" in context:
                enhanced += f"\nDominio NFD: {context['nfd_domain']}"

            # Agregar información del token PANAS
            if "panas_balance" in context:
                enhanced += f"\nBalance PANAS: {context['panas_balance']}"

            # Agregar historial médico si está disponible
            if "medical_history" in context:
                enhanced += f"\nHistorial médico: {context['medical_history']}"

        # Agregar capacidades específicas del asistente
        enhanced += f"\n\nCapacidades disponibles: {', '.join(assistant.capabilities)}"

        return enhanced

    async def get_all_assistants_info(self) -> Dict[str, Any]:
        """Obtener información de todos los asistentes médicos"""
        return {
            "assistants": [
                {
                    "type": key,
                    "name": assistant.name,
                    "specialty": assistant.specialty,
                    "description": assistant.description,
                    "capabilities": assistant.capabilities,
                    "url": assistant.url
                }
                for key, assistant in self.assistants.items()
            ],
            "total_assistants": len(self.assistants)
        }

    async def route_medical_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enrutar consulta médica al asistente más apropiado
        """
        # Palabras clave para enrutamiento automático
        routing_keywords = {
            "clinica_vaser": [
                "vaser", "liposucción", "grasa", "procedimiento estético",
                "cirugía plástica", "tratamiento", "precio", "costo"
            ],
            "medico_vaser": [
                "médico", "evaluación", "preoperatorio", "postoperatorio",
                "complicación", "protocolo", "historia clínica"
            ],
            "liliana_gpt": [
                "cita", "coordinación", "horario", "información",
                "atención", "soporte", "administrativo"
            ]
        }

        query_lower = query.lower()
        best_match = "liliana_gpt"  # Por defecto
        max_matches = 0

        # Encontrar el asistente con más coincidencias
        for assistant_type, keywords in routing_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = assistant_type

        logger.info(f"Enrutando consulta a {best_match} (coincidencias: {max_matches})")

        return await self.get_assistant_response(best_match, query, context)

# Instancia global
medical_gpt = MedicalGPTIntegration()

async def main():
    """Función de prueba"""
    # Ejemplo de uso
    response = await medical_gpt.route_medical_query(
        "¿Cuánto cuesta un procedimiento Vaser?",
        context={"user_id": "test_user", "nfd_domain": "10.panas.algo"}
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

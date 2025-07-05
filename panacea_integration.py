"""
Cliente de integración con Panacea API Central

Este módulo proporciona integración con la API central de Panacea en Heroku
para conectar el proyecto panas_token con el pipeline de APIs.
"""

import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class PanaceaAPIClient:
    """Cliente para interactuar con la API central de Panacea."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializar el cliente de Panacea API.

        Args:
            base_url: URL base de la API de Panacea. Por defecto desde .env
            api_key: Clave API si es necesaria para autenticación
        """
        self.base_url = base_url or os.getenv("PANACEA_API_URL", "https://panacea-api-central.herokuapp.com")
        self.api_key = api_key or os.getenv("PANACEA_API_KEY")

        # Modo fallback para cuando Panacea no esté disponible
        self.fallback_mode = os.getenv("PANACEA_FALLBACK_MODE", "true").lower() == "true"

        # Configurar headers por defecto
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "PanasToken/1.0"
        }

        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _is_panacea_available(self) -> bool:
        """Verificar si Panacea API está disponible."""
        return not (self.base_url.startswith("https://your-panacea") or
                   self.base_url.startswith("https://panacea-api-central.herokuapp.com"))

    async def _fallback_response(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Respuesta de fallback cuando Panacea no está disponible."""
        return {
            "status": "fallback",
            "operation": operation,
            "message": "Panacea API no disponible, usando respuesta simulada",
            "data": data,
            "fallback": True,
            "timestamp": datetime.now().isoformat()
        }

    async def chat_with_ai(self, prompt: str) -> Dict[str, Any]:
        """
        Enviar un prompt al endpoint de chat de Panacea.

        Args:
            prompt: Mensaje para enviar al sistema de IA

        Returns:
            Respuesta del sistema de chat
        """
        if self.fallback_mode and not self._is_panacea_available():
            return await self._fallback_response("chat_with_ai", {"prompt": prompt})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/",
                    json={"prompt": prompt},
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Error al conectar con Panacea Chat API: {e}")

    async def analyze_surgery_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analizar riesgo quirúrgico usando el simulador de Panacea.

        Args:
            patient_data: Datos del paciente para análisis

        Returns:
            Análisis de riesgo quirúrgico
        """
        if self.fallback_mode and not self._is_panacea_available():
            return await self._fallback_response("analyze_surgery_risk", patient_data)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/sim/risk/",
                    json=patient_data,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Error al conectar con Panacea Risk API: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Verificar el estado de salud de la API de Panacea.

        Returns:
            Estado de la API
        """
        if self.fallback_mode and not self._is_panacea_available():
            return await self._fallback_response("get_health_status", {})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"status": "error", "message": str(e)}

    async def submit_token_analysis(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enviar datos del token PANAS para análisis en el pipeline.

        Args:
            token_data: Datos del token para análisis

        Returns:
            Resultado del análisis
        """
        # Estructurar datos específicos para el token PANAS
        payload = {
            "token_name": "PANAS",
            "token_type": "algorand",
            "analysis_type": "medical_token",
            "data": token_data
        }

        if self.fallback_mode and not self._is_panacea_available():
            return await self._fallback_response("submit_token_analysis", payload)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/analyze/token/",
                    json=payload,
                    headers=self.headers,
                    timeout=45.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Error al enviar análisis de token: {e}")


class PanaceaIntegrationService:
    """Servicio de integración que combina IA local y API de Panacea."""

    def __init__(self):
        """Inicializar el servicio de integración."""
        self.panacea_client = PanaceaAPIClient()

        # Configuración del token PANAS
        self.token_config = {
            "name": "PANAS",
            "network": os.getenv("ALGORAND_NETWORK", "testnet"),
            "total_supply": os.getenv("PANAS_TOTAL_SUPPLY", "1000000"),
            "decimals": int(os.getenv("PANAS_DECIMALS", "6")),
            "use_case": "medical_research_incentive"
        }

    async def analyze_medical_data_with_ai(self, medical_prompt: str) -> Dict[str, Any]:
        """
        Analizar datos médicos usando la IA de Panacea.

        Args:
            medical_prompt: Prompt relacionado con datos médicos

        Returns:
            Análisis de IA especializado en medicina
        """
        enhanced_prompt = f"""
        Como token PANAS para investigación médica, analiza:
        {medical_prompt}

        Contexto: Token de incentivos para investigación médica en blockchain Algorand.
        Enfoque: Aplicaciones prácticas en salud y medicina.
        """

        return await self.panacea_client.chat_with_ai(enhanced_prompt)

    async def evaluate_research_participant_risk(self, participant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluar riesgo de participante en investigación médica.

        Args:
            participant_data: Datos del participante

        Returns:
            Evaluación de riesgo
        """
        # Adaptar datos para el formato de Panacea
        adapted_data = {
            "age": participant_data.get("age", 0),
            "gender": participant_data.get("gender", "unknown"),
            "medical_history": participant_data.get("medical_history", []),
            "current_medications": participant_data.get("medications", []),
            "research_type": participant_data.get("research_type", "general"),
            "consent_level": participant_data.get("consent_level", "basic")
        }

        return await self.panacea_client.analyze_surgery_risk(adapted_data)

    async def submit_panas_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enviar métricas del token PANAS al pipeline de análisis.

        Args:
            metrics: Métricas del token y su uso

        Returns:
            Análisis de las métricas
        """
        token_metrics = {
            **self.token_config,
            "metrics": metrics,
            "timestamp": metrics.get("timestamp"),
            "network_stats": {
                "transactions": metrics.get("transaction_count", 0),
                "active_users": metrics.get("active_users", 0),
                "research_projects": metrics.get("research_projects", 0)
            }
        }

        return await self.panacea_client.submit_token_analysis(token_metrics)

    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Obtener estado de la integración con Panacea.

        Returns:
            Estado de conectividad y servicios
        """
        health_status = await self.panacea_client.get_health_status()

        return {
            "panacea_api_status": health_status,
            "token_config": self.token_config,
            "integration_ready": health_status.get("status") == "ok",
            "available_services": [
                "medical_ai_analysis",
                "risk_evaluation",
                "token_metrics_analysis"
            ]
        }

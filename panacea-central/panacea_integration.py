#!/usr/bin/env python3
"""
Integración PANAS Token con Panacea API Central
Conecta el ecosistema PANAS con el repositorio central de Panacea
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from loguru import logger
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PanaceaEndpoint:
    """Configuración de endpoints de Panacea API Central"""
    name: str
    path: str
    method: str
    description: str
    requires_auth: bool = True

# Endpoints principales de Panacea API Central
PANACEA_ENDPOINTS = {
    "health": PanaceaEndpoint("Health Check", "/health", "GET", "Estado de la API", False),
    "auth": PanaceaEndpoint("Authentication", "/auth/login", "POST", "Autenticación de usuarios", False),
    "users": PanaceaEndpoint("User Management", "/users", "GET", "Gestión de usuarios", True),
    "medical_records": PanaceaEndpoint("Medical Records", "/medical/records", "GET", "Registros médicos", True),
    "consultations": PanaceaEndpoint("Medical Consultations", "/medical/consultations", "POST", "Consultas médicas", True),
    "appointments": PanaceaEndpoint("Appointments", "/appointments", "GET", "Gestión de citas", True),
    "medical_assets": PanaceaEndpoint("Medical Assets", "/assets/medical", "GET", "Activos médicos tokenizados", True),
    "nfd_integration": PanaceaEndpoint("NFD Integration", "/nfd/domains", "GET", "Integración NFDomains", True),
    "panas_tokens": PanaceaEndpoint("PANAS Tokens", "/tokens/panas", "GET", "Gestión tokens PANAS", True),
    "ai_services": PanaceaEndpoint("AI Services", "/ai/medical", "POST", "Servicios de IA médica", True),
}

class PanaceaAPIIntegration:
    """Integración con Panacea API Central"""
    
    def __init__(self):
        self.base_url = os.getenv("PANACEA_API_URL", "http://panacea-api-central:8000")
        self.panas_api_url = os.getenv("PANAS_API_URL", "http://panas-api:8000")
        self.medical_gpt_url = os.getenv("MEDICAL_GPT_API_URL", "http://medical-gpt-api:5003")
        self.api_key = os.getenv("PANACEA_API_KEY", "")
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Autenticar con Panacea API Central"""
        try:
            auth_data = {
                "username": username,
                "password": password,
                "client_id": "panas-token-integration"
            }
            
            response = await self._make_request("POST", "/auth/login", data=auth_data, auth_required=False)
            
            if response.get("success"):
                self.auth_token = response.get("access_token")
                logger.info("Autenticación exitosa con Panacea API Central")
                return response
            else:
                logger.error(f"Error en autenticación: {response.get('error')}")
                return {"success": False, "error": "Authentication failed"}
                
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_user_data(self, user_id: str, panas_data: Dict) -> Dict[str, Any]:
        """Sincronizar datos de usuario entre PANAS y Panacea"""
        try:
            sync_payload = {
                "user_id": user_id,
                "panas_balance": panas_data.get("balance", 0),
                "nfd_domains": panas_data.get("nfd_domains", []),
                "medical_consultations": panas_data.get("consultations", []),
                "last_sync": datetime.utcnow().isoformat(),
                "source": "panas-token-system"
            }
            
            response = await self._make_request("POST", f"/users/{user_id}/sync", data=sync_payload)
            
            if response.get("success"):
                logger.info(f"Sincronización exitosa para usuario {user_id}")
                return response
            else:
                logger.warning(f"Error en sincronización: {response.get('error')}")
                return response
                
        except Exception as e:
            logger.error(f"Error sincronizando usuario {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_medical_consultation(self, consultation_data: Dict) -> Dict[str, Any]:
        """Crear consulta médica en Panacea API Central"""
        try:
            # Enriquecer datos con información de PANAS
            enriched_data = {
                **consultation_data,
                "panas_token_reward": self._calculate_consultation_reward(consultation_data),
                "nfd_domain": consultation_data.get("nfd_domain"),
                "integration_source": "panas-telegram-bot",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self._make_request("POST", "/medical/consultations", data=enriched_data)
            
            if response.get("success"):
                # Notificar sistema PANAS sobre la nueva consulta
                await self._notify_panas_consultation(response["consultation_id"], consultation_data)
                
            return response
            
        except Exception as e:
            logger.error(f"Error creando consulta médica: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_medical_assets(self, user_id: str) -> Dict[str, Any]:
        """Obtener activos médicos tokenizados del usuario"""
        try:
            response = await self._make_request("GET", f"/assets/medical?user_id={user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error obteniendo activos médicos: {e}")
            return {"success": False, "error": str(e)}
    
    async def register_nfd_domain(self, domain_data: Dict) -> Dict[str, Any]:
        """Registrar dominio NFD en Panacea Central"""
        try:
            nfd_payload = {
                "domain_name": domain_data["domain"],
                "owner_address": domain_data.get("owner"),
                "domain_type": domain_data.get("type"),
                "properties": domain_data.get("properties", {}),
                "panas_integration": True,
                "registration_timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self._make_request("POST", "/nfd/domains", data=nfd_payload)
            return response
            
        except Exception as e:
            logger.error(f"Error registrando dominio NFD: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_ai_medical_response(self, query: str, context: Dict) -> Dict[str, Any]:
        """Obtener respuesta de IA médica integrada"""
        try:
            ai_payload = {
                "query": query,
                "context": context,
                "integration_source": "panas-medical-gpt",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self._make_request("POST", "/ai/medical", data=ai_payload)
            return response
            
        except Exception as e:
            logger.error(f"Error en consulta IA médica: {e}")
            return {"success": False, "error": str(e)}
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """Realizar petición a Panacea API Central"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth_required and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif auth_required and not self.auth_token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, **result}
                else:
                    error_text = await response.text()
                    logger.error(f"API Error {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_consultation_reward(self, consultation_data: Dict) -> float:
        """Calcular recompensa PANAS por consulta médica"""
        base_reward = 10.0
        
        # Bonus por tipo de consulta
        consultation_type = consultation_data.get("type", "general")
        type_multipliers = {
            "vaser": 2.0,
            "medical_specialist": 1.5,
            "appointment": 1.2,
            "general": 1.0
        }
        
        reward = base_reward * type_multipliers.get(consultation_type, 1.0)
        
        # Bonus por dominio NFD
        if consultation_data.get("nfd_domain"):
            reward *= 1.1
        
        return round(reward, 2)
    
    async def _notify_panas_consultation(self, consultation_id: str, consultation_data: Dict):
        """Notificar al sistema PANAS sobre nueva consulta"""
        try:
            notification_data = {
                "consultation_id": consultation_id,
                "user_id": consultation_data.get("user_id"),
                "reward_amount": self._calculate_consultation_reward(consultation_data),
                "event_type": "medical_consultation"
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                f"{self.panas_api_url}/events/consultation",
                json=notification_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Notificación PANAS enviada para consulta {consultation_id}")
                else:
                    logger.warning(f"Error notificando PANAS: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error notificando PANAS: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de Panacea API Central"""
        return await self._make_request("GET", "/health", auth_required=False)
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Obtener estado de la integración"""
        try:
            health = await self.health_check()
            
            return {
                "panacea_api_status": "healthy" if health.get("success") else "error",
                "panas_integration": True,
                "medical_gpt_integration": True,
                "nfd_integration": True,
                "available_endpoints": list(PANACEA_ENDPOINTS.keys()),
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "panacea_api_status": "error",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

# Instancia global
panacea_integration = PanaceaAPIIntegration()

async def main():
    """Función de prueba"""
    async with PanaceaAPIIntegration() as integration:
        # Test health check
        health = await integration.health_check()
        print(f"Health Check: {health}")
        
        # Test integration status
        status = await integration.get_integration_status()
        print(f"Integration Status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())

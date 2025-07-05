#!/usr/bin/env python3
"""
NFDomains Integration for PANAS Token
Integración con dominios NFDomains de Algorand
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger

@dataclass
class NFDomain:
    """Representación de un dominio NFD"""
    name: str
    owner: str
    resolver: Optional[str]
    properties: Dict[str, Any]
    expiry: Optional[str]

class NFDomainsAPI:
    """Cliente para la API de NFDomains"""

    def __init__(self, base_url: str = "https://api.nf.domains"):
        self.base_url = base_url
        self.session = None

        # Dominios PANAS registrados
        self.panas_domains = {
            "10.panas.algo": {
                "url": "https://app.nf.domains/name/10.panas.algo",
                "purpose": "Dominio principal PANAS Token",
                "type": "main"
            },
            "tokenizado.algo": {
                "url": "https://app.nf.domains/name/tokenizado.algo",
                "purpose": "Servicios de tokenización",
                "type": "service"
            },
            "panacea.icono.algo": {
                "url": "https://app.nf.domains/name/panacea.icono.algo",
                "purpose": "Panacea Icon - Marca visual",
                "type": "brand"
            },
            "activo.algo": {
                "url": "https://app.nf.domains/name/activo.algo",
                "purpose": "Gestión de activos digitales",
                "type": "asset"
            }
        }

        # URL del dominio web principal
        self.web_domain = "https://boliviachic.com"

    async def _get_session(self):
        """Obtener sesión HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()

    async def get_domain_info(self, domain_name: str) -> Optional[NFDomain]:
        """Obtener información de un dominio NFD"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/nfd/{domain_name}"

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "PANAS-Token-Bot/1.0"
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return NFDomain(
                        name=data.get("name", domain_name),
                        owner=data.get("owner", ""),
                        resolver=data.get("resolver"),
                        properties=data.get("properties", {}),
                        expiry=data.get("expiry")
                    )
                else:
                    logger.warning(f"NFD API returned {response.status} for {domain_name}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching NFD info for {domain_name}: {e}")
            return None

    async def verify_domain_ownership(self, domain_name: str, expected_owner: str) -> bool:
        """Verificar propiedad de un dominio"""
        domain_info = await self.get_domain_info(domain_name)
        if domain_info:
            return domain_info.owner.lower() == expected_owner.lower()
        return False

    async def get_all_panas_domains(self) -> Dict[str, Dict]:
        """Obtener información de todos los dominios PANAS"""
        results = {}

        for domain_name, domain_info in self.panas_domains.items():
            nfd_info = await self.get_domain_info(domain_name)
            results[domain_name] = {
                **domain_info,
                "nfd_data": nfd_info.__dict__ if nfd_info else None,
                "status": "active" if nfd_info else "inactive"
            }

        return results

    async def resolve_domain_to_address(self, domain_name: str) -> Optional[str]:
        """Resolver dominio a dirección Algorand"""
        domain_info = await self.get_domain_info(domain_name)
        if domain_info and domain_info.resolver:
            return domain_info.resolver
        return None

    async def get_domain_properties(self, domain_name: str) -> Dict[str, Any]:
        """Obtener propiedades de un dominio"""
        domain_info = await self.get_domain_info(domain_name)
        if domain_info:
            return domain_info.properties
        return {}

    def get_panas_domain_list(self) -> List[Dict]:
        """Obtener lista de dominios PANAS con información"""
        return [
            {
                "domain": name,
                "nfd_url": info["url"],
                "purpose": info["purpose"],
                "type": info["type"],
                "web_access": self.web_domain if info["type"] == "main" else None
            }
            for name, info in self.panas_domains.items()
        ]

class NFDTelegramIntegration:
    """Integración de NFDomains con Telegram Bots"""

    def __init__(self, nfd_api: NFDomainsAPI):
        self.nfd_api = nfd_api

    async def format_domain_info_message(self, domain_name: str) -> str:
        """Formatear información de dominio para mensaje de Telegram"""
        if domain_name not in self.nfd_api.panas_domains:
            return f"❌ Dominio {domain_name} no está en la lista de dominios PANAS"

        domain_config = self.nfd_api.panas_domains[domain_name]
        nfd_info = await self.nfd_api.get_domain_info(domain_name)

        message = f"""
🌐 **Dominio NFD: {domain_name}**

📋 **Información:**
• Propósito: {domain_config['purpose']}
• Tipo: {domain_config['type'].title()}
• URL NFD: {domain_config['url']}

"""

        if nfd_info:
            message += f"""
✅ **Estado: Activo**
• Owner: `{nfd_info.owner[:8]}...{nfd_info.owner[-8:]}`
• Resolver: `{nfd_info.resolver or 'No configurado'}`

"""
        else:
            message += "❌ **Estado: No encontrado o inactivo**\n\n"

        if domain_config['type'] == 'main':
            message += f"🌍 **Acceso Web:** {self.nfd_api.web_domain}\n"

        return message

    async def get_all_domains_status_message(self) -> str:
        """Obtener mensaje con estado de todos los dominios PANAS"""
        domains_info = await self.nfd_api.get_all_panas_domains()

        message = """
🌐 **Dominios NFD de PANAS Token**

"""

        for domain_name, info in domains_info.items():
            status_emoji = "✅" if info["status"] == "active" else "❌"
            message += f"{status_emoji} **{domain_name}**\n"
            message += f"   • {info['purpose']}\n"
            message += f"   • Tipo: {info['type'].title()}\n\n"

        message += f"🌍 **Sitio Web Principal:** {self.nfd_api.web_domain}\n"
        message += "\n💡 Usa `/domain <nombre>` para ver detalles específicos"

        return message

    async def search_domain_by_type(self, domain_type: str) -> str:
        """Buscar dominios por tipo"""
        filtered_domains = [
            (name, info) for name, info in self.nfd_api.panas_domains.items()
            if info["type"] == domain_type.lower()
        ]

        if not filtered_domains:
            return f"❌ No se encontraron dominios de tipo '{domain_type}'"

        message = f"🔍 **Dominios tipo '{domain_type.title()}':**\n\n"

        for domain_name, info in filtered_domains:
            message += f"🌐 **{domain_name}**\n"
            message += f"   • {info['purpose']}\n"
            message += f"   • URL: {info['url']}\n\n"

        return message

# Instancia global para usar en los bots
nfd_api = NFDomainsAPI()
nfd_telegram = NFDTelegramIntegration(nfd_api)

async def cleanup_nfd_resources():
    """Limpiar recursos de NFDomains"""
    await nfd_api.close()

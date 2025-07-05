#!/usr/bin/env python3
"""
Integración específica con dominios NFD de PANAS Token
Maneja los dominios: 10.panas.algo, tokenizado.algo, panacea.icono.algo, activo.algo
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from loguru import logger
import json

# Dominios NFD específicos de PANAS
PANAS_NFD_DOMAINS = {
    "10.panas.algo": {
        "url": "https://app.nf.domains/name/10.panas.algo",
        "type": "main",
        "description": "Dominio principal PANAS Token",
        "purpose": "Token principal y governance",
        "features": ["governance", "staking", "rewards"]
    },
    "tokenizado.algo": {
        "url": "https://app.nf.domains/name/tokenizado.algo",
        "type": "tokenization",
        "description": "Dominio para tokenización de activos médicos",
        "purpose": "Tokenización de investigación médica y activos",
        "features": ["tokenization", "medical_assets", "research_tokens"]
    },
    "panacea.icono.algo": {
        "url": "https://app.nf.domains/name/panacea.icono.algo",
        "type": "medical",
        "description": "Dominio médico especializado",
        "purpose": "Servicios médicos y plataforma Panacea",
        "features": ["medical_services", "consultations", "health_records"]
    },
    "activo.algo": {
        "url": "https://app.nf.domains/name/activo.algo",
        "type": "assets",
        "description": "Dominio para gestión de activos",
        "purpose": "Gestión y trading de activos tokenizados",
        "features": ["asset_management", "trading", "portfolio"]
    }
}

# URL base para NFDomains API
NFD_API_BASE = "https://api.nf.domains/nfd"
BOLIVIACHIC_WEBSITE = "https://boliviachic.com"

class PanasNFDManager:
    """Gestor de dominios NFD específicos de PANAS"""
    
    def __init__(self):
        self.domains = PANAS_NFD_DOMAINS
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """Obtener información detallada de un dominio NFD"""
        if domain_name not in self.domains:
            raise ValueError(f"Dominio no registrado: {domain_name}")
        
        domain_config = self.domains[domain_name]
        
        try:
            # Intentar obtener información de la API NFD
            nfd_data = await self._fetch_nfd_api_data(domain_name)
            
            # Combinar con configuración local
            result = {
                "domain": domain_name,
                "config": domain_config,
                "nfd_data": nfd_data,
                "status": "active" if nfd_data else "unknown",
                "last_updated": "2025-01-05"  # Timestamp actual
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo info del dominio {domain_name}: {e}")
            return {
                "domain": domain_name,
                "config": domain_config,
                "error": str(e),
                "status": "error"
            }
    
    async def _fetch_nfd_api_data(self, domain_name: str) -> Optional[Dict]:
        """Obtener datos de la API NFDomains"""
        try:
            url = f"{NFD_API_BASE}/{domain_name}"
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API NFD retornó {response.status} para {domain_name}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error consultando API NFD para {domain_name}: {e}")
            return None
    
    async def get_all_domains_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los dominios PANAS"""
        results = {}
        
        for domain_name in self.domains.keys():
            results[domain_name] = await self.get_domain_info(domain_name)
        
        return {
            "domains": results,
            "total_domains": len(results),
            "website": BOLIVIACHIC_WEBSITE,
            "nfd_registry": "https://app.nf.domains"
        }
    
    async def get_domain_by_type(self, domain_type: str) -> List[Dict[str, Any]]:
        """Obtener dominios por tipo (main, tokenization, medical, assets)"""
        matching_domains = []
        
        for domain_name, config in self.domains.items():
            if config.get("type") == domain_type:
                domain_info = await self.get_domain_info(domain_name)
                matching_domains.append(domain_info)
        
        return matching_domains
    
    async def search_domains_by_feature(self, feature: str) -> List[Dict[str, Any]]:
        """Buscar dominios por característica específica"""
        matching_domains = []
        
        for domain_name, config in self.domains.items():
            if feature in config.get("features", []):
                domain_info = await self.get_domain_info(domain_name)
                matching_domains.append(domain_info)
        
        return matching_domains
    
    async def get_medical_domains(self) -> List[Dict[str, Any]]:
        """Obtener dominios relacionados con servicios médicos"""
        medical_features = ["medical_services", "consultations", "health_records", "medical_assets"]
        medical_domains = []
        
        for feature in medical_features:
            domains = await self.search_domains_by_feature(feature)
            medical_domains.extend(domains)
        
        # Eliminar duplicados
        seen = set()
        unique_domains = []
        for domain in medical_domains:
            domain_name = domain["domain"]
            if domain_name not in seen:
                seen.add(domain_name)
                unique_domains.append(domain)
        
        return unique_domains
    
    def get_domain_telegram_info(self, domain_name: str) -> str:
        """Generar información de dominio para Telegram"""
        if domain_name not in self.domains:
            return f"❌ Dominio no encontrado: {domain_name}"
        
        config = self.domains[domain_name]
        
        message = f"🌐 **{domain_name}**\n\n"
        message += f"📝 {config['description']}\n"
        message += f"🎯 **Propósito:** {config['purpose']}\n\n"
        message += "✨ **Características:**\n"
        
        for feature in config['features']:
            feature_emoji = {
                "governance": "🏛️",
                "staking": "💰",
                "rewards": "🎁",
                "tokenization": "🪙",
                "medical_assets": "🏥",
                "research_tokens": "🔬",
                "medical_services": "👨‍⚕️",
                "consultations": "💬",
                "health_records": "📋",
                "asset_management": "📊",
                "trading": "📈",
                "portfolio": "💼"
            }.get(feature, "•")
            
            feature_name = feature.replace("_", " ").title()
            message += f"{feature_emoji} {feature_name}\n"
        
        message += f"\n🔗 [Ver en NFDomains]({config['url']})"
        message += f"\n🌍 [Sitio Web Principal]({BOLIVIACHIC_WEBSITE})"
        
        return message

# Instancia global
panas_nfd = PanasNFDManager()

async def main():
    """Función de prueba"""
    async with PanasNFDManager() as manager:
        # Obtener información de todos los dominios
        all_domains = await manager.get_all_domains_status()
        print(json.dumps(all_domains, indent=2, ensure_ascii=False))
        
        # Obtener dominios médicos
        medical_domains = await manager.get_medical_domains()
        print(f"\nDominios médicos encontrados: {len(medical_domains)}")

if __name__ == "__main__":
    asyncio.run(main())

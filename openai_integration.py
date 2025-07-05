"""
Ejemplo de integración de OpenAI con AlgoKit

Este módulo muestra cómo integrar OpenAI con el proyecto AlgoKit.
Incluye ejemplos de uso básico de la API de OpenAI y soporte para Ollama (IA local).
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()


class AIService:
    """Servicio para interactuar con APIs de IA (OpenAI u Ollama)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializar el servicio de IA.

        Args:
            api_key: Clave API de OpenAI. Si no se proporciona, se lee de las variables de entorno.
            model: Modelo a usar. Si no se proporciona, se lee de las variables de entorno.
        """
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or self._get_default_model()

        # Configuraciones desde .env
        self.algorand_network = os.getenv("ALGORAND_NETWORK", "testnet")
        self.algorand_node_url = os.getenv("ALGORAND_NODE_URL")
        self.algorand_indexer_url = os.getenv("ALGORAND_INDEXER_URL")

        # Configuración Ollama
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_enabled = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

        # Inicializar cliente apropiado
        if self.ai_provider == "ollama" and self.ollama_enabled:
            self.client = None  # Usaremos requests para Ollama
        else:
            if not self.api_key:
                raise ValueError(
                    "Se requiere una clave API de OpenAI. Establece OPENAI_API_KEY en tu .env"
                )
            self.client = OpenAI(api_key=self.api_key)

    def _get_default_model(self) -> str:
        """Obtener el modelo por defecto según el proveedor."""
        if self.ai_provider == "ollama":
            return os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def _call_ollama(
        self, messages: list, max_tokens: int = 500, temperature: float = 0.7
    ) -> str:
        """Llamar a la API de Ollama."""
        try:
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("response", "No se pudo generar respuesta")
        except Exception as e:
            raise Exception(f"Error al conectar con Ollama: {e}")

    async def _call_openai(
        self, messages: list, max_tokens: int = 500, temperature: float = 0.7
    ) -> str:
        """Llamar a la API de OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=max_tokens, temperature=temperature
        )
        return response.choices[0].message.content

    async def generate_smart_contract_description(
        self, contract_name: str, functionality: str
    ) -> str:
        """
        Generar una descripción de smart contract usando IA.

        Args:
            contract_name: Nombre del contrato inteligente
            functionality: Descripción de la funcionalidad del contrato

        Returns:
            Descripción generada del smart contract
        """
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en smart contracts de Algorand. Ayudas a generar descripciones técnicas detalladas.",
            },
            {
                "role": "user",
                "content": f"""
                Crea una descripción técnica detallada para un smart contract llamado '{contract_name}'
                con la siguiente funcionalidad: {functionality}

                Incluye:
                - Propósito del contrato
                - Funciones principales
                - Estados globales necesarios
                - Consideraciones de seguridad
                """,
            },
        ]

        if self.ai_provider == "ollama" and self.ollama_enabled:
            return await self._call_ollama(messages)
        else:
            return await self._call_openai(messages)

    async def analyze_contract_code(self, code: str) -> str:
        """
        Analizar código de smart contract usando IA.

        Args:
            code: Código del smart contract

        Returns:
            Análisis del código
        """
        messages = [
            {
                "role": "system",
                "content": "Eres un auditor de smart contracts de Algorand. Analiza el código y proporciona feedback constructivo.",
            },
            {
                "role": "user",
                "content": f"""
                Analiza el siguiente código de smart contract de Algorand:

                ```python
                {code}
                ```

                Proporciona:
                1. Resumen del contrato
                2. Posibles vulnerabilidades
                3. Mejoras sugeridas
                4. Buenas prácticas aplicadas
                """,
            },
        ]

        if self.ai_provider == "ollama" and self.ollama_enabled:
            return await self._call_ollama(messages)
        else:
            return await self._call_openai(messages)

    async def generate_test_cases(self, contract_description: str) -> str:
        """
        Generar casos de prueba para un smart contract.

        Args:
            contract_description: Descripción del contrato

        Returns:
            Casos de prueba sugeridos
        """
        messages = [
            {
                "role": "system",
                "content": "Eres un especialista en testing de smart contracts. Generas casos de prueba comprehensivos.",
            },
            {
                "role": "user",
                "content": f"""
                Basándote en esta descripción de smart contract:
                {contract_description}

                Genera casos de prueba que incluyan:
                1. Casos de éxito (happy path)
                2. Casos de error
                3. Casos edge
                4. Pruebas de seguridad
                """,
            },
        ]

        if self.ai_provider == "ollama" and self.ollama_enabled:
            return await self._call_ollama(messages)
        else:
            return await self._call_openai(messages)


async def main():
    """Función principal para demostrar el uso del servicio de IA."""
    print("🚀 Iniciando integración con IA para PANAS Token...")

    try:
        # Inicializar servicio de IA
        ai_service = AIService()
        print(f"🤖 Usando proveedor: {ai_service.ai_provider}")
        print(f"📋 Modelo: {ai_service.model}")
        print(f"🌐 Red de Algorand: {ai_service.algorand_network}")

        # Ejemplo 1: Generar descripción de contrato
        print("\n📝 Generando descripción de smart contract...")
        description = await ai_service.generate_smart_contract_description(
            "PanasToken",
            "Token fungible que representa la moneda PANAS con funcionalidades de transferencia, mint y burn",
        )
        print(f"📄 Descripción generada:\n{description}")

        # Ejemplo 2: Analizar código de contrato
        sample_code = """
        from pyteal import *
        from beaker import Application, AccountStateValue, GlobalStateValue

        class PanasToken(Application):
            total_supply = GlobalStateValue(
                stack_type=TealType.uint64,
                default=Int(0),
                descr="Total supply of PANAS tokens"
            )

            def create_token(self):
                return Seq([
                    self.total_supply.set(Int(1000000)),
                    Approve()
                ])

            def transfer(self, amount, receiver):
                return Seq([
                    Assert(amount > Int(0)),
                    # Transfer logic here
                    Approve()
                ])
        """

        print("\n🔍 Analizando código de smart contract...")
        analysis = await ai_service.analyze_contract_code(sample_code)
        print(f"📊 Análisis:\n{analysis}")

        # Ejemplo 3: Generar casos de prueba
        print("\n🧪 Generando casos de prueba...")
        test_cases = await ai_service.generate_test_cases(description)
        print(f"🧪 Casos de prueba sugeridos:\n{test_cases}")

    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        print("💡 Verifica tu configuración en el archivo .env")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

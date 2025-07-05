"""
Ejemplo de uso de la integración con Panacea API Central

Este script demuestra cómo usar el cliente de Panacea para integrar
el token PANAS con el pipeline de APIs médicas.
"""

import asyncio
import json
from datetime import datetime

from dotenv import load_dotenv

from panacea_integration import PanaceaIntegrationService

load_dotenv()


async def main():
    """Función principal para demostrar la integración."""
    print("🏥 Iniciando integración PANAS Token con Panacea API Central...")

    # Inicializar servicio de integración
    panacea_service = PanaceaIntegrationService()

    try:
        # 1. Verificar estado de la integración
        print("\n📊 Verificando estado de la integración...")
        status = await panacea_service.get_integration_status()
        print(f"Estado: {json.dumps(status, indent=2)}")

        # 2. Ejemplo de análisis médico con IA
        print("\n🤖 Analizando datos médicos con IA de Panacea...")
        medical_prompt = """
        Analiza la viabilidad de un token de incentivos para participantes
        en estudios clínicos de medicamentos experimentales para enfermedades raras.
        Considera aspectos éticos, legales y de seguridad.
        """

        ai_analysis = await panacea_service.analyze_medical_data_with_ai(medical_prompt)
        print(f"Análisis de IA: {json.dumps(ai_analysis, indent=2)}")

        # 3. Ejemplo de evaluación de riesgo de participante
        print("\n⚕️ Evaluando riesgo de participante en investigación...")
        participant_data = {
            "age": 45,
            "gender": "female",
            "medical_history": ["diabetes", "hypertension"],
            "medications": ["metformin", "lisinopril"],
            "research_type": "clinical_trial_phase_2",
            "consent_level": "informed_consent",
        }

        risk_evaluation = await panacea_service.evaluate_research_participant_risk(participant_data)
        print(f"Evaluación de riesgo: {json.dumps(risk_evaluation, indent=2)}")

        # 4. Ejemplo de envío de métricas del token PANAS
        print("\n📈 Enviando métricas del token PANAS...")
        token_metrics = {
            "timestamp": datetime.now().isoformat(),
            "transaction_count": 1250,
            "active_users": 89,
            "research_projects": 5,
            "total_rewards_distributed": 50000,
            "research_categories": ["oncology", "rare_diseases", "neurology"],
            "geographic_distribution": {"north_america": 45, "europe": 32, "asia": 12},
        }

        metrics_analysis = await panacea_service.submit_panas_metrics(token_metrics)
        print(f"Análisis de métricas: {json.dumps(metrics_analysis, indent=2)}")

        print("\n✅ Integración completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante la integración: {e}")
        print("\n💡 Consejos para solucionar:")
        print("1. Verifica que PANACEA_API_URL esté configurada en .env")
        print("2. Asegúrate de que la API de Panacea esté funcionando")
        print("3. Revisa la conectividad de red")


async def test_individual_endpoints():
    """Probar endpoints individuales para debugging."""
    print("\n🔧 Probando endpoints individuales...")

    service = PanaceaIntegrationService()

    # Test simple de chat
    try:
        simple_response = await service.panacea_client.chat_with_ai(
            "Hola, ¿cómo puedes ayudar con el token PANAS?"
        )
        print(f"✅ Chat endpoint funcionando: {simple_response}")
    except Exception as e:
        print(f"❌ Error en chat endpoint: {e}")

    # Test de estado de salud
    try:
        health = await service.panacea_client.get_health_status()
        print(f"✅ Health endpoint: {health}")
    except Exception as e:
        print(f"❌ Error en health endpoint: {e}")


if __name__ == "__main__":
    print("🚀 Ejecutando ejemplo de integración PANAS-Panacea")
    print("=" * 60)

    # Ejecutar ejemplo principal
    asyncio.run(main())

    # Ejecutar tests individuales si hay errores
    print("\n" + "=" * 60)
    asyncio.run(test_individual_endpoints())

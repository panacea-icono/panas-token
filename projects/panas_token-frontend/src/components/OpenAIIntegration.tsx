import OpenAI from 'openai'
import React, { useState } from 'react'

// Nota: En producción, las llamadas a OpenAI deberían hacerse desde el backend por seguridad
// Este es solo un ejemplo para propósitos de demostración

interface OpenAIComponentProps {
  apiKey?: string
}

const OpenAIIntegration: React.FC<OpenAIComponentProps> = ({ apiKey }) => {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Inicializar cliente OpenAI
  const openai = apiKey
    ? new OpenAI({
        apiKey: apiKey,
        dangerouslyAllowBrowser: true, // Solo para desarrollo, NO usar en producción
      })
    : null

  const generateSmartContractAnalysis = async () => {
    if (!openai) {
      setError('OpenAI API key no configurada')
      return
    }

    if (!prompt.trim()) {
      setError('Por favor ingresa una descripción del contrato')
      return
    }

    setLoading(true)
    setError('')

    try {
      const completion = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content:
              'Eres un experto en desarrollo de smart contracts para Algorand. Ayuda a los desarrolladores a crear contratos seguros y eficientes.',
          },
          {
            role: 'user',
            content: `Analiza y proporciona recomendaciones para un smart contract de Algorand con la siguiente descripción: ${prompt}`,
          },
        ],
        max_tokens: 500,
        temperature: 0.7,
      })

      setResponse(completion.choices[0].message.content || 'No se generó respuesta')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card w-full bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">🤖 Análisis de Smart Contract con IA</h2>

        {!apiKey && (
          <div className="alert alert-warning">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.88-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <span>Configure su clave API de OpenAI para usar esta funcionalidad</span>
          </div>
        )}

        <div className="form-control">
          <label className="label">
            <span className="label-text">Describe tu smart contract:</span>
          </label>
          <textarea
            className="textarea textarea-bordered h-24"
            placeholder="Ej: Un contrato de votación descentralizada con múltiples opciones..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={!apiKey || loading}
          />
        </div>

        <div className="card-actions justify-end">
          <button
            className={`btn btn-primary ${loading ? 'loading' : ''}`}
            onClick={generateSmartContractAnalysis}
            disabled={!apiKey || loading || !prompt.trim()}
          >
            {loading ? 'Analizando...' : 'Analizar con IA'}
          </button>
        </div>

        {error && (
          <div className="alert alert-error mt-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {response && (
          <div className="mt-4">
            <h3 className="font-bold text-lg mb-2">📋 Análisis generado:</h3>
            <div className="bg-base-200 p-4 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm">{response}</pre>
            </div>
          </div>
        )}

        <div className="mt-4 text-sm text-base-content/70">
          <p>
            ⚠️ <strong>Nota de seguridad:</strong> En una aplicación de producción, las llamadas a OpenAI deben realizarse desde el backend
            para proteger la clave API.
          </p>
        </div>
      </div>
    </div>
  )
}

export default OpenAIIntegration

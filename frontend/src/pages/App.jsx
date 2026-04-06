import { useEffect, useState } from 'react'
import { apiFetch } from '../api/client'
import { Disclaimer } from '../components/Disclaimer'

export function App() {
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('secret123')
  const [isAuth, setIsAuth] = useState(Boolean(localStorage.getItem('token')))
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [summary, setSummary] = useState(null)
  const [selectedMeal, setSelectedMeal] = useState(null)
  const [error, setError] = useState('')

  async function registerOrLogin(mode) {
    setError('')
    try {
      const data = await apiFetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('token', data.access_token)
      setIsAuth(true)
      await loadSummary()
    } catch (e) {
      setError(e.message)
    }
  }

  async function loadSummary() {
    try {
      const data = await apiFetch('/api/meals/daily/summary')
      setSummary(data)
      if (data.meals?.length > 0) setSelectedMeal(data.meals[0])
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    if (isAuth) loadSummary()
  }, [isAuth])

  async function analyze() {
    if (!file) return
    setStatus('processing')
    setError('')
    try {
      const formData = new FormData()
      formData.append('image', file)
      const job = await apiFetch('/api/meals/analyze', { method: 'POST', body: formData })
      const meal = await apiFetch(`/api/meals/${job.meal_id}`)
      setSelectedMeal(meal)
      await loadSummary()
      setStatus('done')
    } catch (e) {
      setStatus('idle')
      setError(e.message)
    }
  }

  async function updateItem(itemId, payload) {
    if (!selectedMeal) return
    const updated = await apiFetch(`/api/meals/${selectedMeal.id}/items/${itemId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    setSelectedMeal(updated)
    await loadSummary()
  }

  if (!isAuth) {
    return (
      <main className="container">
        <h1>Meal Vision MVP</h1>
        <p>Registro/Login simple para comenzar.</p>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
        <div className="row">
          <button onClick={() => registerOrLogin('register')}>Registrar</button>
          <button onClick={() => registerOrLogin('login')}>Ingresar</button>
        </div>
        {error && <p className="error">{error}</p>}
      </main>
    )
  }

  return (
    <main className="container">
      <h1>Meal Vision MVP</h1>
      <Disclaimer />

      <section className="card">
        <h2>Subir foto del plato</h2>
        <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={analyze}>Analizar comida</button>
        {status === 'processing' && <p>🔄 Análisis en curso...</p>}
      </section>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Historial del día</h2>
        <p>Total calorías: <strong>{summary?.total_calories || 0} kcal</strong></p>
        <ul>
          {summary?.meals?.map((meal) => (
            <li key={meal.id}>
              <button className="link" onClick={() => setSelectedMeal(meal)}>
                #{meal.id} - {meal.total_calories} kcal - confianza {Math.round((meal.confidence || 0) * 100)}%
              </button>
            </li>
          ))}
        </ul>
      </section>

      {selectedMeal && (
        <section className="card">
          <h2>Revisión antes de confirmar</h2>
          <p>Calorías totales: {selectedMeal.total_calories} kcal</p>
          <p>Confianza: {Math.round((selectedMeal.confidence || 0) * 100)}%</p>

          <div className="items">
            {selectedMeal.items.map((item) => (
              <div key={item.id} className="item">
                <input
                  defaultValue={item.normalized_food_name}
                  onBlur={(e) => updateItem(item.id, { normalized_food_name: e.target.value })}
                />
                <input
                  type="number"
                  defaultValue={item.corrected_grams || item.estimated_grams}
                  onBlur={(e) => updateItem(item.id, { corrected_grams: Number(e.target.value) })}
                />
                <span>{item.calories} kcal</span>
                <button onClick={() => updateItem(item.id, { remove: true })}>Eliminar</button>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  )
}

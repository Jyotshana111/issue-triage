import { useState } from 'react'

import './App.css'

function App() {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, body }),
      })

      if (!response.ok) throw new Error(`Request failed: ${response.status}`)
      setResult(await response.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>Issue Triage Assistant</h1>
      <p>Enter a GitHub issue title to suggest a label and find similar issues.</p>

      <form onSubmit={handleSubmit}>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Enter an issue title"
          required
        />
        <label htmlFor="issue-body">Description (optional)</label>
        <textarea
          id="issue-body"
          value={body}
          onChange={(event) => setBody(event.target.value)}
          placeholder="Describe what happened"
          rows={5}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {result && (
        <section>
          <h2>Suggested label: {result.suggested_label}</h2>
          <h3>Similar issues</h3>
          <ul>
            {result.similar_issues.map((issue) => (
              <li key={issue.url}>
                <a href={issue.url} target="_blank" rel="noreferrer">
                  {issue.title}
                </a>
                {' — score: '}{issue.score}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}

export default App

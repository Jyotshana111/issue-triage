import { useState } from 'react'
import './App.css'

const examples = [
  { kind: 'Bug report', title: 'read_csv crashes when the file has an empty header', body: 'Reading a CSV file with an empty header raises an error instead of returning a DataFrame.' },
  { kind: 'Documentation', title: 'Add an example for reading compressed CSV files', body: 'The read_csv documentation should include a short example using a gzip compressed file.' },
  { kind: 'Enhancement', title: 'Support a custom date format in read_csv', body: 'Allow users to pass a date format when parsing a column in read_csv.' },
]

function Icon({ name, size = 20 }) {
  const shapes = {
    spark: <><path d="m12 2 1.9 6.1L20 10l-6.1 1.9L12 18l-1.9-6.1L4 10l6.1-1.9L12 2Z" /><path d="m19 17 .7 1.3L21 19l-1.3.7L19 21l-.7-1.3L17 19l1.3-.7L19 17Z" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    external: <><path d="M13 5h6v6" /><path d="m19 5-9 9" /><path d="M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5" /></>,
    copy: <><rect x="8" y="8" width="11" height="11" rx="2" /><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    layers: <><rect x="3" y="4" width="18" height="5" rx="1" /><rect x="3" y="11" width="18" height="5" rx="1" /><path d="M7 20h10" /></>,
    branch: <><circle cx="7" cy="6" r="2" /><circle cx="17" cy="18" r="2" /><circle cx="7" cy="18" r="2" /><path d="M7 8v8m2-10h4a4 4 0 0 1 4 4v6" /></>,
    shield: <><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" /><path d="m9 12 2 2 4-4" /></>,
  }
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>
}

function App() {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  function chooseExample(example) {
    setTitle(example.title)
    setBody(example.body)
    setResult(null)
    setError('')
    setCopied(false)
    document.getElementById('issue-title')?.focus()
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    setCopied(false)
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim(), body: body.trim() }),
      })
      if (!response.ok) throw new Error('The analysis service returned ' + response.status + '. Please try again.')
      setResult(await response.json())
    } catch (err) {
      setError(err instanceof TypeError
        ? 'Could not reach the analysis service. Check that the Python and Java servers are running.'
        : err.message)
    } finally {
      setLoading(false)
    }
  }

  async function copySummary() {
    if (!result) return
    const lines = [
      'Issue: ' + title.trim(),
      'Suggested label: ' + result.suggested_label,
      '',
      'Related issues:',
      ...result.similar_issues.map((issue) => '- ' + issue.title + ' (' + issue.url + ')'),
    ]
    try {
      await navigator.clipboard.writeText(lines.join('\n'))
      setCopied(true)
    } catch {
      setError('Could not copy the summary. Please check your browser clipboard permissions.')
    }
  }

  const relatedIssues = result?.similar_issues ?? []

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Project information">
        <a className="brand" href="#top" aria-label="Issue Triage home"><span className="brand-mark"><Icon name="spark" size={22} /></span><span>triage<span className="brand-light">.ai</span></span></a>
        <nav className="sidebar-group" aria-label="On this page">
          <p className="sidebar-heading">WORKSPACE</p>
          <a className="sidebar-link active" href="#analyze"><Icon name="layers" size={18} /> Analyze issue</a>
          <a className="sidebar-link" href="#how-it-works"><Icon name="branch" size={18} /> How it works</a>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note"><span className="note-icon"><Icon name="shield" size={18} /></span><strong>Human in the loop</strong><p>Suggestions help maintainers review issues. They do not make final triage decisions.</p></div>
          <a className="source-link" href="https://github.com/Jyotshana111/issue-triage" target="_blank" rel="noreferrer">View source on GitHub <Icon name="external" size={15} /></a>
        </div>
      </aside>

      <main id="top" className="main-content">
        <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <strong>Issue analyzer</strong></div><div className="topbar-tag"><span className="status-dot" /> Interactive demo</div></header>
        <div className="page-content">
          <section className="hero" aria-labelledby="hero-title">
            <div className="hero-copy">
              <span className="eyebrow"><Icon name="spark" size={15} /> AI-POWERED ISSUE TRIAGE</span>
              <h1 id="hero-title">From issue report<br />to clear next steps.</h1>
              <p>Suggest a label and discover related pandas issues in one thoughtful workflow.</p>
              <a className="hero-link" href="#analyze">Try the analyzer <Icon name="arrow" size={17} /></a>
            </div>
            <div className="hero-art" aria-hidden="true"><span className="orbit orbit-one" /><span className="orbit orbit-two" /><span className="orbit orbit-three" /><span className="orbit-node node-one" /><span className="orbit-node node-two" /><span className="orbit-node node-three" /><span className="hero-core"><Icon name="spark" size={34} /></span><span className="hero-mini-card card-one">BUG <span>↗</span></span><span className="hero-mini-card card-two">Related issue</span></div>
          </section>

          <div className="section-heading" id="analyze"><div><span className="section-kicker">01 / ANALYZE</span><h2>Analyze an issue</h2><p>Paste an issue or choose an example to see the workflow.</p></div><span className="section-count">1,000 issues indexed</span></div>
          <div className="content-grid">
            <section className="analyze-card" aria-label="Issue analysis form">
              <div className="card-heading"><span className="card-icon"><Icon name="layers" size={19} /></span><div><h3>Issue details</h3><p>More context can improve related issue search.</p></div></div>
              <form onSubmit={handleSubmit}>
                <label htmlFor="issue-title">Issue title <span className="required">*</span></label>
                <input id="issue-title" value={title} onChange={(event) => { setTitle(event.target.value); setResult(null) }} placeholder="e.g. read_csv crashes on an empty header" maxLength={300} disabled={loading} required />
                <div className="label-row"><label htmlFor="issue-body">Description <span className="optional">Optional</span></label><span className="character-count">{body.length} characters</span></div>
                <textarea id="issue-body" value={body} onChange={(event) => { setBody(event.target.value); setResult(null) }} placeholder="What happened? What did you expect instead?" rows={5} disabled={loading} />
                <div className="form-footer"><span><Icon name="shield" size={15} /> Review suggestions before applying labels</span><button className="primary-button" type="submit" disabled={loading || !title.trim()}>{loading ? <><span className="spinner" /> Analyzing...</> : <><Icon name="spark" size={18} /> Analyze issue <Icon name="arrow" size={17} /></>}</button></div>
              </form>
              {error && <div className="error-message" role="alert">{error}</div>}
            </section>

            <aside className="examples-card" aria-labelledby="examples-title">
              <div className="examples-heading"><span className="examples-icon"><Icon name="spark" size={18} /></span><div><h3 id="examples-title">Try an example</h3><p>Start with a realistic issue</p></div></div>
              <div className="example-list">{examples.map((example, index) => <button className="example-button" type="button" key={example.kind} disabled={loading} onClick={() => chooseExample(example)}><span className="example-number">0{index + 1}</span><span><strong>{example.kind}</strong><small>{example.title}</small></span><Icon name="arrow" size={16} /></button>)}</div>
              <div className="examples-tip"><Icon name="shield" size={17} /><span>The model suggests a label; a maintainer makes the final call.</span></div>
            </aside>
          </div>

          <section className="results-section" aria-live="polite" aria-busy={loading}>
            {loading && <div className="loading-card"><span className="spinner dark" /><div><h3>Analyzing the issue</h3><p>Classifying the report and searching related issues...</p></div></div>}
            {result && <>
              <div className="section-heading results-heading"><div><span className="section-kicker">02 / RESULTS</span><h2>Your analysis</h2><p>A starting point for faster, more informed triage.</p></div><button className="copy-button" type="button" onClick={copySummary}><Icon name={copied ? 'check' : 'copy'} size={17} /> {copied ? 'Copied' : 'Copy summary'}</button></div>
              <div className="result-grid"><div className="label-card"><span className="result-overline">SUGGESTED LABEL</span><div className={'label-badge label-' + result.suggested_label.toLowerCase().replace(/[^a-z]/g, '')}><span className="label-dot" />{result.suggested_label}</div><p>Predicted from the issue title and description. Review it before applying.</p></div><div className="match-card"><span className="result-overline">RELATED ISSUES</span><strong>{relatedIssues.length.toString().padStart(2, '0')}</strong><p>Potentially relevant reports from the indexed pandas collection.</p></div></div>
              <div className="issues-card"><div className="issues-header"><div><h3>Related issues</h3><p>Open a report to check whether it describes the same problem.</p></div><span className="issues-count">{relatedIssues.length} results</span></div>
                {relatedIssues.length ? <ol className="issues-list">{relatedIssues.map((issue, index) => <li key={issue.url}><span className="issue-rank">{String(index + 1).padStart(2, '0')}</span><div className="issue-info"><a href={issue.url} target="_blank" rel="noreferrer">{issue.title} <Icon name="external" size={16} /></a><span>pandas-dev / pandas</span></div><span className="score-chip">Score {Number(issue.score).toFixed(3)}</span></li>)}</ol> : <p className="empty-matches">No related issues were returned for this report.</p>}
                <div className="score-note"><Icon name="shield" size={17} /><span>Similarity scores measure text closeness. They are not duplicate probabilities; always inspect the linked issue.</span></div>
              </div>
            </>}
          </section>

          <section className="how-section" id="how-it-works" aria-labelledby="how-title"><div className="section-heading"><div><span className="section-kicker">BEHIND THE SCENES</span><h2 id="how-title">How it works</h2><p>A small full-stack system with practical machine learning.</p></div></div><div className="steps-grid"><div className="step-card"><span>01</span><h3>Describe</h3><p>Enter a title and optional context for a GitHub issue.</p></div><div className="step-card"><span>02</span><h3>Classify</h3><p>A trained model suggests Bug, Docs, or Enhancement.</p></div><div className="step-card"><span>03</span><h3>Compare</h3><p>Sentence embeddings rank related issues for human review.</p></div></div></section>
          <footer>Built with React, Spring Boot, FastAPI &amp; sentence embeddings <span>·</span> <a href="https://github.com/Jyotshana111/issue-triage" target="_blank" rel="noreferrer">Explore the code <Icon name="external" size={14} /></a></footer>
        </div>
      </main>
    </div>
  )
}

export default App

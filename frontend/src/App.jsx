import { useState } from 'react'
import './App.css'//imports the css file

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`${API_URL}/reel/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, action: 'download' }),
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'Download failed')
      }

      const videoBlob = await response.blob()
      const downloadUrl = URL.createObjectURL(videoBlob)

      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = 'reel.mp4'
      link.click()

      window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000)
      setSuccess('Your Reel is ready and downloading.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <section className="card">
        <h1>ReelBridge</h1>
        <p>Share reels beyond Instagram</p>

        <form onSubmit={handleSubmit}>
          <input
            className="reelInput"
            type="url"
            placeholder="Paste Instagram Reel URL"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Preparing Reel...' : 'Get Reel'}
          </button>
        </form>

        {error && <p role="alert">{error}</p>}
        {success && <p role="status">{success}</p>}
      </section>
    </main>
  )
}

export default App

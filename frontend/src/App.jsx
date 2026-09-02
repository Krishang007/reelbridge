import { useState } from 'react'
import './App.css'//imports the css file

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [action, setAction] = useState("download");
  const isSendAction = action === 'discord' || action === 'whatsapp'

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    // expetionhanplign and fecths 
    try {
      const response = await fetch('http://localhost:8000/reel/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
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

      URL.revokeObjectURL(downloadUrl)
    } catch (err) {
      setError(err.message)
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

          <select
            value={action}
            onChange={(event) => setAction(event.target.value)}
          >
            <option value="download">Download</option>
            <option value="discord">Discord</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="text">Text</option>
          </select>

          <button type="submit" disabled={loading}>
            {loading
              ? (isSendAction ? 'Sending...' : 'Getting Reel...')
              : (isSendAction ? 'Send Reel' : 'Get Reel')}
          </button>
        </form>

        {error && <p>{error}</p>}
      </section>
    </main>
  )
}

export default App

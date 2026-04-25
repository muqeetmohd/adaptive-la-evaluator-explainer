import React, { useState, useEffect, useRef } from 'react'
import { BookOpen, RotateCcw, Sparkles, Brain, GraduationCap, Layers, ArrowUp } from 'lucide-react'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const API = '/api'

type Stage = 'diagnostic' | 'topic' | 'chat'
type TierNum = 1 | 2 | 3

interface Message {
  role: 'user' | 'assistant'
  content: string
  tier?: TierNum
  sources?: string[]
  loading?: boolean
}

const TIER_META: Record<TierNum, { label: string; color: string; bg: string; border: string; icon: React.ReactNode }> = {
  1: { label: 'Geometric Intuition',    color: '#4ade80', bg: 'rgba(74,222,128,0.1)',  border: 'rgba(74,222,128,0.25)', icon: <Brain size={11} /> },
  2: { label: 'Formal Beginner',        color: '#60a5fa', bg: 'rgba(96,165,250,0.1)',  border: 'rgba(96,165,250,0.25)', icon: <BookOpen size={11} /> },
  3: { label: 'Algebraically Grounded', color: '#f87171', bg: 'rgba(248,113,113,0.1)', border: 'rgba(248,113,113,0.25)', icon: <GraduationCap size={11} /> },
}

function TierBadge({ tier }: { tier: TierNum }) {
  const m = TIER_META[tier]
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{ color: m.color, background: m.bg, border: `1px solid ${m.border}` }}
    >
      {m.icon}{m.label}
    </span>
  )
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 py-1">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-2 h-2 rounded-full animate-bounce"
          style={{ background: '#555770', animationDelay: `${i * 0.18}s` }}
        />
      ))}
    </div>
  )
}

// ── Math rendering ──────────────────────────────────────────────────────────

function renderKatex(tex: string, displayMode: boolean): React.ReactNode {
  try {
    const html = katex.renderToString(tex, {
      displayMode,
      throwOnError: false,
      strict: false,
    })
    return (
      <span
        className={displayMode ? 'block text-center my-2' : 'inline'}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    )
  } catch {
    return <span>{tex}</span>
  }
}

// Split text on math delimiters and inline formatting, return ReactNodes
function inlineRender(text: string): React.ReactNode[] {
  // Order matters: $$ before $, \[ before \(
  const mathPattern = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\$[^$\n]+?\$|\\\([^)]+?\\\))/g
  const segments = text.split(mathPattern)
  const nodes: React.ReactNode[] = []

  segments.forEach((seg, si) => {
    if (seg.startsWith('$$') && seg.endsWith('$$')) {
      nodes.push(<React.Fragment key={si}>{renderKatex(seg.slice(2, -2), true)}</React.Fragment>)
    } else if (seg.startsWith('\\[') && seg.endsWith('\\]')) {
      nodes.push(<React.Fragment key={si}>{renderKatex(seg.slice(2, -2), true)}</React.Fragment>)
    } else if (seg.startsWith('$') && seg.endsWith('$')) {
      nodes.push(<React.Fragment key={si}>{renderKatex(seg.slice(1, -1), false)}</React.Fragment>)
    } else if (seg.startsWith('\\(') && seg.endsWith('\\)')) {
      nodes.push(<React.Fragment key={si}>{renderKatex(seg.slice(2, -2), false)}</React.Fragment>)
    } else {
      // Handle bold, italic, inline code
      seg.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g).forEach((p, pi) => {
        if (p.startsWith('`') && p.endsWith('`')) {
          nodes.push(
            <code key={`${si}-${pi}`} style={{ padding: '1px 6px', borderRadius: 4, fontSize: '0.85em', fontFamily: 'monospace', background: 'rgba(108,99,255,0.18)', color: '#a78bfa' }}>
              {p.slice(1, -1)}
            </code>
          )
        } else if (p.startsWith('**') && p.endsWith('**')) {
          nodes.push(<strong key={`${si}-${pi}`} style={{ color: '#ececf1', fontWeight: 600 }}>{p.slice(2, -2)}</strong>)
        } else if (p.startsWith('*') && p.endsWith('*')) {
          nodes.push(<em key={`${si}-${pi}`} style={{ color: '#d1d1e0' }}>{p.slice(1, -1)}</em>)
        } else if (p) {
          nodes.push(<React.Fragment key={`${si}-${pi}`}>{p}</React.Fragment>)
        }
      })
    }
  })

  return nodes
}

function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split('\n')
  const out: React.ReactNode[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // Display math block spanning multiple lines: \[ ... \] or $$ ... $$
    if (/^\s*(\$\$|\\\[)/.test(line)) {
      const openDelim = line.includes('$$') ? '$$' : '\\['
      const closeDelim = openDelim === '$$' ? '$$' : '\\]'
      const block: string[] = [line]
      i++
      while (i < lines.length && !lines[i].includes(closeDelim)) {
        block.push(lines[i++])
      }
      if (i < lines.length) block.push(lines[i])
      const raw = block.join('\n').replace(new RegExp(`^\\s*${openDelim.replace('$','\\$').replace('[','\\[')}\\s*`), '').replace(new RegExp(`\\s*${closeDelim.replace('$','\\$').replace(']','\\]')}\\s*$`), '')
      out.push(<div key={i} className="my-3">{renderKatex(raw, true)}</div>)
    } else if (/^#{1,3}\s/.test(line)) {
      const lvl = (line.match(/^(#+)/)?.[1].length ?? 1)
      const sizes = ['text-base font-semibold', 'text-sm font-semibold', 'text-sm font-medium']
      out.push(
        <p key={i} className={`${sizes[Math.min(lvl - 1, 2)]} mt-3 mb-1`} style={{ color: '#ececf1' }}>
          {inlineRender(line.replace(/^#+\s/, ''))}
        </p>
      )
    } else if (/^(\*\*?|-|\d+\.)\s/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^(\*\*?|-|\d+\.)\s/.test(lines[i])) {
        items.push(lines[i].replace(/^(\*\*?|-|\d+\.)\s/, ''))
        i++
      }
      out.push(
        <ul key={`ul${i}`} className="space-y-1 my-2">
          {items.map((it, j) => (
            <li key={j} className="flex gap-2 text-sm leading-relaxed" style={{ color: '#c5c5d2' }}>
              <span style={{ color: '#6c63ff', flexShrink: 0, marginTop: 2 }}>•</span>
              <span>{inlineRender(it)}</span>
            </li>
          ))}
        </ul>
      )
      continue
    } else if (line.trim() === '') {
      out.push(<div key={`br${i}`} className="h-2" />)
    } else {
      out.push(
        <p key={i} className="text-sm leading-relaxed" style={{ color: '#c5c5d2' }}>
          {inlineRender(line)}
        </p>
      )
    }
    i++
  }

  return <>{out}</>
}

// ── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  const [stage, setStage]                 = useState<Stage>('diagnostic')
  const [questions, setQuestions]         = useState<string[]>([])
  const [topics, setTopics]               = useState<string[]>([])
  const [messages, setMessages]           = useState<Message[]>([])
  const [input, setInput]                 = useState('')
  const [diagResponses, setDiagResponses] = useState<string[]>([])
  const [selectedTopic, setSelectedTopic] = useState('')
  const [diagStep, setDiagStep]           = useState(0)
  const [resultTier, setResultTier]       = useState<TierNum | null>(null)
  const [loading, setLoading]             = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef  = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/questions`).then(r => r.json()),
      fetch(`${API}/topics`).then(r => r.json()),
    ]).then(([q, t]) => {
      setQuestions(q.questions)
      setTopics(t.topics)
      setMessages([{ role: 'assistant', content: q.questions[0] }])
    })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function autoResize() {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 180) + 'px'
  }

  async function send() {
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    if (inputRef.current) inputRef.current.style.height = 'auto'

    if (stage === 'diagnostic') {
      const next = [...diagResponses, text]
      setMessages(m => [...m, { role: 'user', content: text }])
      setDiagResponses(next)
      if (next.length < 3) {
        setDiagStep(next.length)
        setTimeout(() => setMessages(m => [...m, { role: 'assistant', content: questions[next.length] }]), 350)
      } else {
        setTimeout(() => {
          setMessages(m => [...m, { role: 'assistant', content: "Great! Now pick a topic below — I'll tailor the explanation to your level." }])
          setStage('topic')
        }, 350)
      }
      return
    }

    if (stage === 'chat') {
      // Add user message + empty loading assistant message
      setMessages(m => [...m,
        { role: 'user', content: text },
        { role: 'assistant', content: '', loading: true },
      ])
      setLoading(true)

      try {
        const res = await fetch(`${API}/session/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_query: text, diagnostic_responses: diagResponses, topic: selectedTopic }),
        })

        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail ?? 'Request failed')
        }

        const reader = res.body!.getReader()
        const decoder = new TextDecoder()
        let buf = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buf += decoder.decode(value, { stream: true })

          const lines = buf.split('\n')
          buf = lines.pop() ?? ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const payload = line.slice(6)
            if (payload === '[DONE]') break

            let event: { type: string; tier?: number; sources?: string[]; text?: string; message?: string }
            try { event = JSON.parse(payload) } catch { continue }

            if (event.type === 'meta') {
              setResultTier(event.tier as TierNum)
              setMessages(m => m.map((msg, i) =>
                i === m.length - 1
                  ? { ...msg, tier: event.tier as TierNum, sources: event.sources }
                  : msg
              ))
            } else if (event.type === 'chunk') {
              setMessages(m => m.map((msg, i) =>
                i === m.length - 1
                  ? { ...msg, content: msg.content + (event.text ?? ''), loading: false }
                  : msg
              ))
            } else if (event.type === 'error') {
              throw new Error(event.message)
            }
          }
        }
      } catch (e: unknown) {
        const err = e instanceof Error ? e.message : 'Unknown error'
        setMessages(m => m.map((msg, i) =>
          i === m.length - 1 ? { role: 'assistant', content: `Error: ${err}` } : msg
        ))
      } finally {
        setLoading(false)
      }
    }
  }

  function pickTopic(topic: string) {
    setSelectedTopic(topic)
    setStage('chat')
    setMessages(m => [...m,
      { role: 'user', content: topic.replace(/_/g, ' ') },
      { role: 'assistant', content: `Let's explore **${topic.replace(/_/g, ' ')}**. What would you like to understand?` },
    ])
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  function reset() {
    setStage('diagnostic')
    setDiagResponses([])
    setDiagStep(0)
    setSelectedTopic('')
    setResultTier(null)
    setInput('')
    setMessages(questions.length ? [{ role: 'assistant', content: questions[0] }] : [])
  }

  const stageIndex = stage === 'diagnostic' ? 0 : stage === 'topic' ? 1 : 2
  const stageLabels = ['Diagnose', 'Pick Topic', 'Explore']

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh', background: '#212121', overflow: 'hidden' }}>

      {/* Header */}
      <div style={{
        flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 16px', height: 56,
        borderBottom: '1px solid #2f2f2f',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg,#6c63ff,#a78bfa)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Layers size={14} color="#fff" />
          </div>
          <span style={{ fontSize: 14, fontWeight: 600, color: '#ececf1', letterSpacing: '-0.01em' }}>Adaptive LA Explainer</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {stageLabels.map((label, i) => {
              const active = stageIndex === i
              const done   = stageIndex > i
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <div style={{
                    width: 20, height: 20, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10, fontWeight: 700,
                    background: done ? '#6c63ff' : active ? 'rgba(108,99,255,0.2)' : 'transparent',
                    border: `1.5px solid ${done || active ? '#6c63ff' : '#3f3f3f'}`,
                    color: done ? '#fff' : active ? '#a78bfa' : '#555',
                    transition: 'all 0.3s',
                  }}>
                    {done ? '✓' : i + 1}
                  </div>
                  <span style={{ fontSize: 11, color: active ? '#ececf1' : done ? '#888' : '#444', fontWeight: active ? 500 : 400 }}>
                    {label}
                  </span>
                  {i < 2 && <span style={{ color: '#333', fontSize: 11, marginLeft: 2 }}>›</span>}
                </div>
              )
            })}
          </div>

          {resultTier && <TierBadge tier={resultTier} />}

          <button
            onClick={reset}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '5px 12px', borderRadius: 8,
              border: '1px solid #3f3f3f', background: 'transparent',
              color: '#888', fontSize: 12, cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'inherit',
            }}
            onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor='#6c63ff'; el.style.color='#a78bfa'; el.style.background='rgba(108,99,255,0.08)' }}
            onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor='#3f3f3f'; el.style.color='#888'; el.style.background='transparent' }}
          >
            <RotateCcw size={11} /> Restart
          </button>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ flexShrink: 0, height: 2, background: '#2f2f2f' }}>
        <div style={{ height: '100%', width: `${(stageIndex / 2) * 100}%`, background: 'linear-gradient(90deg,#6c63ff,#a78bfa)', transition: 'width 0.6s ease' }} />
      </div>

      {/* Messages */}
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '28px 16px' }}>
        <div style={{ maxWidth: 680, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 28 }}>

          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: 12, flexDirection: msg.role === 'user' ? 'row-reverse' : 'row', alignItems: 'flex-start' }}>
              {msg.role === 'assistant' && (
                <div style={{
                  width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                  background: 'linear-gradient(135deg,#6c63ff,#a78bfa)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  marginTop: 2,
                }}>
                  <Sparkles size={14} color="#fff" />
                </div>
              )}

              <div style={{ maxWidth: '75%', minWidth: 0 }}>
                {msg.role === 'user' ? (
                  <div style={{
                    padding: '10px 16px',
                    background: '#2f2f2f',
                    borderRadius: '18px 18px 4px 18px',
                    fontSize: 14, color: '#ececf1', lineHeight: 1.65,
                    wordBreak: 'break-word', whiteSpace: 'pre-wrap',
                  }}>
                    {msg.content}
                  </div>
                ) : (
                  <div style={{ paddingLeft: 4 }}>
                    {msg.loading && !msg.content
                      ? <TypingDots />
                      : renderMarkdown(msg.content)
                    }
                    {msg.tier && (
                      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
                        <TierBadge tier={msg.tier} />
                        {msg.sources && msg.sources.length > 0 && (
                          <span style={{ fontSize: 11, color: '#555' }}>{msg.sources.join(' · ')}</span>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Topic pills */}
          {stage === 'topic' && (
            <div style={{ paddingLeft: 44 }}>
              <p style={{ fontSize: 12, color: '#555', marginBottom: 10 }}>Select a topic to explore</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {topics.map(t => (
                  <button
                    key={t}
                    onClick={() => pickTopic(t)}
                    style={{
                      padding: '7px 14px', borderRadius: 20,
                      border: '1px solid #3f3f3f', background: '#2f2f2f',
                      color: '#b0b0c0', fontSize: 13, cursor: 'pointer',
                      transition: 'all 0.2s', fontFamily: 'inherit',
                    }}
                    onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor='#6c63ff'; el.style.color='#a78bfa'; el.style.background='rgba(108,99,255,0.1)' }}
                    onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor='#3f3f3f'; el.style.color='#b0b0c0'; el.style.background='#2f2f2f' }}
                  >
                    {t.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input bar */}
      {stage !== 'topic' && (
        <div style={{ flexShrink: 0, padding: '12px 16px 20px', background: '#212121' }}>
          <div style={{ maxWidth: 680, margin: '0 auto' }}>
            <div
              style={{
                display: 'flex', alignItems: 'flex-end', gap: 8,
                padding: '10px 12px 10px 16px',
                background: '#2f2f2f', borderRadius: 16,
                border: '1px solid #3f3f3f', transition: 'border-color 0.2s',
              }}
              onFocusCapture={e => (e.currentTarget as HTMLElement).style.borderColor = '#6c63ff'}
              onBlurCapture={e => (e.currentTarget as HTMLElement).style.borderColor = '#3f3f3f'}
            >
              <textarea
                ref={inputRef}
                value={input}
                rows={1}
                onChange={e => { setInput(e.target.value); autoResize() }}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
                }}
                placeholder={
                  stage === 'diagnostic'
                    ? `Answer question ${diagStep + 1} of 3…`
                    : `Ask about ${selectedTopic.replace(/_/g, ' ')}…`
                }
                disabled={loading}
                style={{
                  flex: 1, background: 'transparent', border: 'none', outline: 'none',
                  resize: 'none', color: '#ececf1', fontSize: 14, lineHeight: 1.6,
                  fontFamily: 'inherit', caretColor: '#a78bfa',
                  overflowY: 'auto', maxHeight: 180, paddingTop: 2,
                }}
              />
              <button
                onClick={send}
                disabled={!input.trim() || loading}
                style={{
                  width: 32, height: 32, borderRadius: 8, border: 'none', flexShrink: 0,
                  background: input.trim() && !loading ? 'linear-gradient(135deg,#6c63ff,#a78bfa)' : '#3f3f3f',
                  color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                  transition: 'background 0.2s',
                }}
              >
                <ArrowUp size={15} />
              </button>
            </div>
            <p style={{ textAlign: 'center', fontSize: 11, color: '#444', marginTop: 8 }}>
              {stage === 'diagnostic'
                ? `Diagnostic · step ${diagStep + 1} of 3`
                : `Groq · Llama 3.3 70B · ${selectedTopic.replace(/_/g, ' ')}`}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState, useRef, useEffect, useCallback, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';

interface Waypoint {
  lat: number;
  lng: number;
  label?: string;
}

interface Route {
  waypoints: Waypoint[];
  eta_minutes?: number;
  distance_meters?: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  route?: Route;
  timestamp: Date;
}

interface ChatProps {
  language: string;
}

const API_BASE = '/api/v1/chat';

export default function Chat({ language }: ChatProps) {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: t('chat.welcome'),
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  const sendMessage = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      text: trimmed,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(API_BASE + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, language }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: data.reply,
        route: data.route ?? undefined,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          text: '⚠️ Could not reach the assistant. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, language]);

  return (
    <div className="chat-container" aria-label="Chat with AI assistant">
      <div 
        className="chat-messages" 
        role="log" 
        aria-live="polite" 
        aria-relevant="additions"
        aria-busy={loading}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-bubble ${msg.role}`}
            aria-label={msg.role === 'user' ? 'Your message' : 'Assistant reply'}
          >
            {msg.text}
            {msg.route && msg.route.waypoints.length > 0 && (
              <div className="chat-route" data-testid="route-info">
                <h4>📍 Navigation Route</h4>
                <div className="chat-route-meta">
                  {msg.route.eta_minutes && (
                    <span>{t('chat.eta', { minutes: msg.route.eta_minutes })}</span>
                  )}
                  {msg.route.distance_meters && (
                    <span>{t('chat.distance', { meters: msg.route.distance_meters })}</span>
                  )}
                </div>
                <div className="chat-route-waypoints" data-testid="route-polyline">
                  {msg.route.waypoints.map((wp, i) => (
                    <div className="waypoint" key={i}>
                      <span className="waypoint-dot" aria-hidden="true" />
                      <span>{wp.label ?? `(${wp.lat.toFixed(4)}, ${wp.lng.toFixed(4)})`}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div 
            className="chat-bubble assistant thinking" 
            aria-label="Assistant is thinking"
            role="status"
          >
            {t('chat.thinking')}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-bar" onSubmit={sendMessage}>
        <input
          ref={inputRef}
          id="chat-input"
          className="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('chat.placeholder')}
          aria-label={t('accessibility.chatInput')}
          maxLength={2000}
          autoComplete="off"
          disabled={loading}
        />
        <button
          id="chat-send-btn"
          className="chat-send-btn"
          type="submit"
          disabled={loading || !input.trim()}
          aria-label={t('accessibility.sendButton')}
        >
          {t('chat.send')}
        </button>
      </form>
    </div>
  );
}

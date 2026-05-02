import React, { useState, useEffect, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import apiClient from '../services/apiClient';
import { Send, Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface Message {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [inputFocused, setInputFocused] = useState(false);

  const reduce = useReducedMotion();

  useEffect(() => {
    // Load history
    const loadHistory = async () => {
      try {
        const res = await apiClient.get('/chat');
        setMessages(res.data);
      } catch (e) {
        console.error("Failed to load char history", e);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const res = await apiClient.post('/chat/', {
       content: userMessage
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.content }]);
    } catch (e) {
      console.error("Chat error", e);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto bg-[var(--surface)] backdrop-blur border border-[var(--border)] rounded-2xl overflow-hidden scale-in shadow-xl">
      <div className="p-4 border-b border-[var(--border)] bg-white shrink-0">
        <h2 className="text-xl font-semibold text-[var(--text-strong)]">AI Storytelling Assistant</h2>
        <p className="text-xs text-[var(--text-muted)] mt-1">Chat to brainstorm ideas or discuss storytelling techniques.</p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth pb-20 bg-gradient-to-b from-white to-blue-50">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-[var(--text-muted)] text-sm fade-in">
            Send a message to start brainstorming!
          </div>
        )}
        {messages.map((msg, idx) => (
          <motion.div key={idx} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reduce ? 0 : 0.28, delay: reduce ? 0 : idx * 0.03 }} className={clsx("flex slide-up", msg.role === 'user' ? "justify-end" : "justify-start")}>
            <div className={clsx(
              "max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed shadow-md",
              msg.role === 'user' 
                ? "bg-[var(--accent)] text-white rounded-tr-sm" 
                : "bg-[var(--hover-bg)] border border-[var(--border)] text-[var(--text-primary)] rounded-tl-sm"
            )}>
              {msg.content}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex justify-start slide-up">
            <div className="max-w-[80%] rounded-2xl rounded-tl-sm p-4 text-sm bg-[var(--hover-bg)] border border-[var(--border)] text-[var(--text-primary)] flex items-center shadow-md">
              <Loader2 className="w-4 h-4 animate-spin text-[var(--accent)] mr-2" />
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-white border-t border-[var(--border)] shrink-0">
        <motion.form
          onSubmit={handleSend}
          className="relative flex items-end gap-2 interactive"
          initial={false}
          animate={{}}
        >
          <motion.div
            className="w-full"
            animate={inputFocused ? { y: -2, boxShadow: '0 8px 24px rgba(255,107,154,0.10)' } : { y: 0, boxShadow: 'none' }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder="Ask me anything..."
              onFocus={() => setInputFocused(true)}
              onBlur={() => setInputFocused(false)}
              className="input-field w-full pr-12 disabled:opacity-50"
            />
          </motion.div>

          <motion.button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 bottom-2 p-2 bg-[var(--accent)] hover:bg-[var(--accent-600)] text-white rounded-lg disabled:opacity-50 disabled:bg-[var(--text-muted)] disabled:text-[var(--text-muted)] transition-all"
            whileHover={(!loading && input.trim()) ? { scale: 1.06, y: -2, boxShadow: '0 10px 30px rgba(255,107,154,0.18)' } : {}}
            whileTap={(!loading && input.trim()) ? { scale: 0.96 } : {}}
            aria-label="Send message"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </motion.button>
        </motion.form>
      </div>
    </div>
  );
};

export default Chat;

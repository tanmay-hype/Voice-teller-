import React, { useState, useEffect, useRef } from 'react';
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
      const res = await apiClient.post('/chat', {
        role: 'user',
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
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl overflow-hidden animate-in zoom-in-95 duration-500 shadow-2xl">
      <div className="p-4 border-b border-slate-800 bg-slate-900 shrink-0">
        <h2 className="text-xl font-semibold text-white">AI Storytelling Assistant</h2>
        <p className="text-xs text-slate-400 mt-1">Chat to brainstorm ideas or discuss storytelling techniques.</p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth pb-20">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Send a message to start brainstorming!
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={clsx("flex", msg.role === 'user' ? "justify-end" : "justify-start")}>
            <div className={clsx(
              "max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed",
              msg.role === 'user' 
                ? "bg-blue-600 text-white rounded-tr-sm" 
                : "bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-sm"
            )}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl rounded-tl-sm p-4 text-sm bg-slate-800 border border-slate-700 text-slate-200 flex items-center">
              <Loader2 className="w-4 h-4 animate-spin text-slate-400 mr-2" />
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
        <form onSubmit={handleSend} className="relative flex items-end gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Type your message..."
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 bottom-2 p-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50 disabled:bg-slate-700 disabled:text-slate-400 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;

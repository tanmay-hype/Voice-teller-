// src/pages/Stories.tsx

import React, { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { BookOpen, Plus } from 'lucide-react';

const Stories: React.FC = () => {
  const stories = useStoryStore((s) => s.stories);
  const voices = useStoryStore((s) => s.voices);
  const setStories = useStoryStore((s) => s.setStories);
  const addStory = useStoryStore((s) => s.addStory);

  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [voiceId, setVoiceId] = useState('');
  const [loading, setLoading] = useState(false);

  const reduce = useReducedMotion();

  useEffect(() => {
    apiClient.get('/stories/')
      .then(res => setStories(res.data))
      .catch(() => {});
  }, [setStories]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    try {
      const res = await apiClient.post('/stories/', {
        title,
        content: prompt,
        voice_id: voiceId || null
      });

      addStory(res.data);
      setShowModal(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">

      <div className="flex justify-between items-center">
        <h1 className="text-3xl text-white font-bold">Stories</h1>

        <button
          onClick={() => setShowModal(true)}
          className="bg-emerald-600 px-4 py-2 rounded-xl text-white flex items-center"
        >
          <Plus className="mr-2" /> New Story
        </button>
      </div>

      {/* GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {stories.map((story, i) => (
          <motion.div key={story.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: reduce ? 0 : i * 0.06, duration: 0.45 }}
            whileHover={{ scale: 1.02 }}
            className="relative bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl overflow-hidden group hover:border-slate-700 transition cursor-pointer">

            {/* 🔥 BACKGROUND ICON */}
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
              <BookOpen className="w-24 h-24 text-emerald-500" />
            </div>

            <div className="relative">
              <div className="p-3 bg-emerald-500/10 rounded-xl w-fit">
                <BookOpen className="w-6 h-6 text-emerald-400" />
              </div>

              <h3 className="mt-4 text-white font-semibold">
                {story.title}
              </h3>

              <p className="text-slate-400 text-sm mt-2 line-clamp-3">
                {story.content}
              </p>

              {story.audio_url && (
                <motion.div whileHover={{ scale: 1.02 }} className="mt-4 w-full">
                  <audio controls className="w-full">
                    <source src={`http://localhost:8000${story.audio_url}`} />
                  </audio>
                </motion.div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur">
          <div className="bg-slate-900 p-6 rounded-xl w-full max-w-md">
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                placeholder="Title"
                onChange={e => setTitle(e.target.value)}
                className="w-full bg-slate-800 p-2 text-white rounded"
              />

              <textarea
                placeholder="Prompt"
                onChange={e => setPrompt(e.target.value)}
                className="w-full bg-slate-800 p-2 text-white rounded"
              />

              <select
                onChange={e => setVoiceId(e.target.value)}
                className="w-full bg-slate-800 p-2 text-white rounded"
              >
                <option value="">No voice</option>
                {voices.map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>

              <button className="bg-emerald-600 w-full py-2 rounded">
                {loading ? "Generating..." : "Generate"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Stories;
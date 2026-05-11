// src/pages/Stories.tsx

import React, { useState, useEffect, useRef } from 'react';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { BookOpen, Plus, Trash2, Volume2, Loader2 } from 'lucide-react';

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
  const [selectedStory, setSelectedStory] = useState<any>(null);
  const [selectedVoiceForReading, setSelectedVoiceForReading] = useState<string | null>(null);
  const [playingUrl, setPlayingUrl] = useState<string | null>(null);
  const [ttsLoading, setTtsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

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
  const handleDeleteStory = async (storyId: string) => {
    if (!window.confirm('Are you sure you want to delete this story?')) return;
    
    try {
      await apiClient.delete(`/stories/${storyId}`);
      setStories(stories.filter((s: any) => s.id !== storyId));
      setSelectedStory(null);
    } catch (err) {
      alert('Failed to delete story');
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

        {stories.map((story) => (
          <div key={story.id}
            onClick={() => setSelectedStory(story)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter') setSelectedStory(story); }}
            className="relative bg-purple-100/50 backdrop-blur-md border border-purple-200 rounded-2xl p-6 shadow-xl overflow-hidden group hover:border-purple-300 transition cursor-pointer">

            {/* 🔥 BACKGROUND ICON */}
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
              <BookOpen className="w-24 h-24 text-emerald-500" />
            </div>

            <div className="relative">
              <div className="p-3 bg-emerald-500/10 rounded-xl w-fit">
                <BookOpen className="w-6 h-6 text-emerald-400" />
              </div>

              <h3 className="mt-4 text-black font-bold capitalize">
                {story.title}
              </h3>

              <p className="text-slate-400 text-sm mt-2 line-clamp-3">
                {story.content}
              </p>

              {story.audio_url && (
                <div className="mt-4 w-full">
                  <audio controls className="w-full">
                    <source src={`http://localhost:8000${story.audio_url}`} />
                  </audio>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* MODAL - NEW STORY */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur">
          <div className="bg-slate-900 p-6 rounded-xl w-full max-w-md border border-slate-800">
            <h3 className="text-white text-lg font-semibold mb-4">Generate New Story</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                placeholder="Story Title"
                value={title}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)}
                required
                className="w-full bg-slate-800 p-2 text-white rounded border border-slate-700 focus:border-emerald-500"
              />

              <textarea
                placeholder="Story Prompt (describe what you want the story to be about)"
                value={prompt}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                required
                className="w-full bg-slate-800 p-2 text-white rounded border border-slate-700 focus:border-emerald-500 h-32"
              />

              <div>
                <label className="text-slate-300 text-sm block mb-2">Voice for narration (optional)</label>
                <select
                  value={voiceId}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setVoiceId(e.target.value)}
                  className="w-full bg-slate-800 p-2 text-white rounded border border-slate-700 focus:border-emerald-500"
                >
                  <option value="">Default voice (Piper)</option>
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
                <p className="text-slate-400 text-xs mt-1">
                  {voiceId ? "Using cloned voice (ElevenLabs)" : "Using default voice (Piper)"}
                </p>
              </div>

              <button 
                type="submit"
                disabled={loading}
                className="bg-emerald-600 w-full py-2 rounded text-white font-semibold hover:bg-emerald-700 disabled:opacity-50"
              >
                {loading ? "Generating..." : "Generate Story"}
              </button>
            </form>
            
            <button 
              onClick={() => {
                setShowModal(false);
                setTitle('');
                setPrompt('');
                setVoiceId('');
              }}
              className="mt-3 w-full bg-slate-800 py-2 rounded text-slate-300 hover:text-white"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* VIEW STORY MODAL */}
      {selectedStory && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur z-50">
          <div className="bg-slate-900 p-6 rounded-xl w-full max-w-3xl max-h-[85vh] overflow-y-auto border border-slate-800 shadow-xl">
            {/* Header */}
            <div className="flex justify-between items-start mb-4 pb-4 border-b border-slate-700">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white">{selectedStory.title}</h2>
                <p className="text-sm text-slate-400 mt-1">
                  {selectedStory.created_at ? new Date(selectedStory.created_at).toLocaleString() : ''}
                </p>
              </div>
              <button onClick={() => setSelectedStory(null)} className="text-slate-400 hover:text-white ml-4 text-2xl">×</button>
            </div>

            {/* Story Content */}
            <div className="mt-6 text-slate-200 whitespace-pre-wrap leading-relaxed max-h-[40vh] overflow-y-auto">
              {selectedStory.content}
            </div>

            {/* Existing Audio Player (if already generated with TTS) */}
            {selectedStory.audio_url && (
              <div className="mt-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
                <p className="text-xs text-slate-400 mb-2">Existing Narration</p>
                <audio controls className="w-full">
                  <source src={`http://localhost:8000${selectedStory.audio_url}`} />
                </audio>
              </div>
            )}

            {/* READ ALOUD SECTION - FLOW */}
            <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-emerald-500/30">
              <div className="flex items-center gap-2 mb-4">
                <Volume2 className="w-5 h-5 text-emerald-400" />
                <h3 className="font-semibold text-white">Read Aloud</h3>
              </div>
              
              <div className="space-y-3">
                {/* Voice Selection */}
                <div>
                  <label className="text-xs text-slate-400 block mb-2">Select voice</label>
                  <select
                    value={selectedVoiceForReading || ''}
                    onChange={(e) => setSelectedVoiceForReading(e.target.value || null)}
                    className="w-full bg-slate-700 p-2 text-white rounded border border-slate-600 focus:border-emerald-500 text-sm"
                  >
                    <option value="">Default voice (Piper - Free)</option>
                    {voices.map(v => (
                      <option key={v.id} value={v.id}>{v.name} (Cloned - ElevenLabs)</option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-500 mt-1">
                    {selectedVoiceForReading 
                      ? "🤖 Using ElevenLabs cloned voice" 
                      : "🎙️ Using Piper (free, local)"}
                  </p>
                </div>

                {/* Read Aloud Button */}
                <button
                  onClick={async () => {
                    setTtsLoading(true);
                    try {
                      const res = await apiClient.post('/stories/read', {
                        text: selectedStory.content,
                        voice_id: selectedVoiceForReading || null,
                        story_id: selectedStory.id
                      });

                      const apiRoot = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/?api\/?$/i, '').replace(/\/$/, '');
                      const url = res.data.url.startsWith('/') ? `${apiRoot}${res.data.url}` : res.data.url;

                      // Stop previous audio
                      if (audioRef.current) {
                        audioRef.current.pause();
                        audioRef.current.src = '';
                        audioRef.current = null;
                        setIsPlaying(false);
                      }

                      const audioEl = new Audio(url);
                      audioRef.current = audioEl;
                      setPlayingUrl(url);
                      audioEl.play();
                      setIsPlaying(true);
                      audioEl.onended = () => {
                        setIsPlaying(false);
                        setPlayingUrl(null);
                        audioRef.current = null;
                      };
                    } catch (err) {
                      console.error('Failed to generate audio', err);
                      alert('Failed to generate audio. Check console for details.');
                    } finally {
                      setTtsLoading(false);
                    }
                  }}
                  disabled={ttsLoading}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 px-4 py-2 rounded text-white font-semibold flex items-center justify-center gap-2"
                >
                  {ttsLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  {ttsLoading ? 'Generating...' : 'Read Aloud'}
                </button>

                {/* Play/Pause for current audio */}
                {playingUrl && (
                  <button
                    onClick={() => {
                      if (!audioRef.current) return;
                      if (isPlaying) {
                        audioRef.current.pause();
                        setIsPlaying(false);
                      } else {
                        audioRef.current.play();
                        setIsPlaying(true);
                      }
                    }}
                    className="w-full bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded text-white font-semibold"
                  >
                    {isPlaying ? '⏸ Pause' : '▶ Resume'}
                  </button>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex justify-end items-center space-x-3">
              <button
                onClick={() => handleDeleteStory(selectedStory.id)}
                className="px-4 py-2 bg-red-600/10 hover:bg-red-600/20 rounded text-red-400 hover:text-red-300 flex items-center gap-2 border border-red-500/30"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>

              <button 
                onClick={() => {
                  setSelectedStory(null);
                  setSelectedVoiceForReading(null);
                }}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Stories;
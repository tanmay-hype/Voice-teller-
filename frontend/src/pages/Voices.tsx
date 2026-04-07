import React, { useState } from 'react';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { BookOpen, Plus, X, Loader2, PlayCircle } from 'lucide-react';

const Stories: React.FC = () => {
  const { stories, voices, addStory } = useStoryStore();
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [voiceId, setVoiceId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !prompt) return;

    setLoading(true);
    try {
      const res = await apiClient.post('/stories', {
        title,
        content: prompt, // sending prompt as content
        voice_id: voiceId || null
      });
      addStory(res.data);
      setShowModal(false);
      setTitle('');
      setPrompt('');
      setVoiceId('');
    } catch (error) {
      console.error("Failed to generate story", error);
      alert("Failed to generate story");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Stories</h1>
          <p className="mt-2 text-slate-400">Generate and listen to AI-powered stories.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg shadow-lg flex items-center transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Generate Story
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stories.map((story) => (
          <div key={story.id} className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-5 flex flex-col hover:border-slate-700 transition-colors">
            <div className="flex items-start justify-between">
              <div className="p-3 bg-emerald-500/10 rounded-lg shrink-0">
                <BookOpen className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
            <h3 className="mt-4 text-lg font-semibold text-white">{story.title}</h3>
            <p className="mt-2 text-sm text-slate-400 line-clamp-3 flex-1">
              {story.content}
            </p>
            {story.audio_url && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <audio controls className="w-full h-10 rounded-lg bg-slate-800">
                  <source src={`http://localhost:8000${story.audio_url}`} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
            {!story.audio_url && story.voice_id && (
              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center text-sm text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Generating audio...
              </div>
            )}
          </div>
        ))}
        {stories.length === 0 && (
          <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-800 rounded-2xl">
            <BookOpen className="mx-auto h-12 w-12 text-slate-600" />
            <h3 className="mt-2 text-sm font-semibold text-white">No stories</h3>
            <p className="mt-1 text-sm text-slate-400">Get started by generating a new story.</p>
          </div>
        )}
      </div>

      {/* Generate Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center p-6 border-b border-slate-800">
              <h3 className="text-lg font-semibold text-white">Generate New Story</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300">Story Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="mt-1 block w-full bg-slate-800 border-slate-700 rounded-lg text-white px-3 py-2 text-sm focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="The Magic Forest"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300">Story Prompt / Idea</label>
                <textarea
                  required
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="mt-1 block w-full bg-slate-800 border-slate-700 rounded-lg text-white px-3 py-2 text-sm focus:ring-emerald-500 focus:border-emerald-500"
                  rows={4}
                  placeholder="Write a short story about a brave knight exploring a dark cave filled with glowing mushrooms."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300">Select Voice (Optional)</label>
                <select
                  value={voiceId}
                  onChange={(e) => setVoiceId(e.target.value)}
                  className="mt-1 block w-full bg-slate-800 border-slate-700 rounded-lg text-white px-3 py-2 text-sm focus:ring-emerald-500 focus:border-emerald-500"
                >
                  <option value="">No voice (Text only)</option>
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>
              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 px-4 border border-slate-700 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors text-sm font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex justify-center py-2 px-4 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Generate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Stories;

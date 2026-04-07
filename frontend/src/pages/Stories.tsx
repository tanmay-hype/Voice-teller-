import React, { useState } from 'react';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { BookOpen, Plus, X, Loader2 } from 'lucide-react';

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
        content: prompt,
        voice_id: voiceId || null,
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
    <div className="space-y-6 max-w-6xl mx-auto px-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Stories
          </h1>
          <p className="text-slate-400 mt-2">
            Generate and listen to AI-powered stories.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-lg text-white flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          Generate
        </button>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {stories.map((story) => (
          <div
            key={story.id}
            className="group bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 flex flex-col hover:border-emerald-500/50 hover:shadow-xl hover:shadow-emerald-500/10 transition-all"
          >
            <BookOpen className="text-emerald-400" />

            <h3 className="mt-4 text-lg font-semibold text-white">
              {story.title}
            </h3>

            <p className="text-slate-400 text-sm mt-2 flex-1 line-clamp-3">
              {story.content}
            </p>

            {/* Audio */}
            {story.audio_url && (
              <audio controls className="mt-4">
                <source
                  src={`http://localhost:8000${story.audio_url}`}
                />
              </audio>
            )}

            {!story.audio_url && story.voice_id !== undefined && (
              <div className="mt-4 flex items-center text-sm text-slate-500">
                <Loader2 className="animate-spin w-4 h-4 mr-2" />
                Generating audio...
              </div>
            )}
          </div>
        ))}

        {stories.length === 0 && (
          <div className="col-span-full text-center py-12 border-2 border-dashed border-slate-800 rounded-2xl">
            <BookOpen className="mx-auto h-12 w-12 text-slate-600" />
            <p className="text-slate-400 mt-2">No stories yet</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-white text-lg mb-4">Generate Story</h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title"
                className="w-full bg-slate-800 px-3 py-2 rounded text-white"
              />

              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Story prompt..."
                className="w-full bg-slate-800 px-3 py-2 rounded text-white"
              />

              <select
                value={voiceId}
                onChange={(e) => setVoiceId(e.target.value)}
                className="w-full bg-slate-800 px-3 py-2 rounded text-white"
              >
                <option value="">No voice</option>
                {voices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>

              <button
                type="submit"
                disabled={loading || !title || !prompt}
                className="w-full bg-emerald-600 hover:bg-emerald-500 py-2 rounded text-white flex justify-center"
              >
                {loading ? <Loader2 className="animate-spin" /> : 'Generate'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
 
export default Stories;
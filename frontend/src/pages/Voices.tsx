import React, { useState } from 'react';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { Mic2, Plus, X, Loader2 } from 'lucide-react';

const Voices: React.FC = () => {
  const { voices, addVoice } = useStoryStore();
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      formData.append('file', file);

      const res = await apiClient.post('/voices', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      addVoice(res.data);
      setShowModal(false);
      setName('');
      setDescription('');
      setFile(null);
    } catch (error) {
      console.error("Failed to upload voice", error);
      alert("Failed to upload voice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Voices</h1>
          <p className="mt-2 text-slate-400">Manage your cloned voices for storytelling.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-lg flex items-center transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Clone New Voice
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {voices.map((voice) => (
          <div key={voice.id} className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors">
            <div className="flex items-start justify-between relative">
              <div className="p-3 bg-blue-500/10 rounded-lg shrink-0">
                <Mic2 className="w-6 h-6 text-blue-400" />
              </div>
              <span className="text-xs font-medium text-slate-500 absolute top-0 right-0">ID: {voice.elevenlabs_voice_id?.substring(0,8)}...</span>
            </div>
            <h3 className="mt-4 text-lg font-semibold text-white">{voice.name}</h3>
            <p className="mt-1 text-sm text-slate-400 line-clamp-2">
              {voice.description || 'No description provided.'}
            </p>
          </div>
        ))}
        {voices.length === 0 && (
          <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-800 rounded-2xl">
            <Mic2 className="mx-auto h-12 w-12 text-slate-600" />
            <h3 className="mt-2 text-sm font-semibold text-white">No voices</h3>
            <p className="mt-1 text-sm text-slate-400">Get started by cloning a new voice.</p>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center p-6 border-b border-slate-800">
              <h3 className="text-lg font-semibold text-white">Clone a New Voice</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300">Voice Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 block w-full bg-slate-800 border-slate-700 rounded-lg text-white px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g. Narrator, Uncle Bob"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="mt-1 block w-full bg-slate-800 border-slate-700 rounded-lg text-white px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="A deep, calm voice perfect for bedtime stories."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300">Audio Sample</label>
                <input
                  type="file"
                  required
                  accept="audio/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="mt-1 block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500"
                />
                <p className="mt-1 text-xs text-slate-500">Must be a clean audio file under 5MB.</p>
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
                  className="flex-1 flex justify-center py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Clone Voice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Voices;

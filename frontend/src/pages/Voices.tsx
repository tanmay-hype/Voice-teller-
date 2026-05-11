// src/pages/Voices.tsx

import React, { useState, useEffect } from 'react';
import { useStoryStore } from '../store/storyStore';
import apiClient from '../services/apiClient';
import { Mic2, Plus } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const Voices: React.FC = () => {
  const voices = useStoryStore((s) => s.voices);
  const setVoices = useStoryStore((s) => s.setVoices);
  const addVoice = useStoryStore((s) => s.addVoice);
  const location = useLocation();

  const [showModal, setShowModal] = useState(location.pathname.includes('/voices/new'));
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiClient.get('/voices/')
      .then(res => setVoices(res.data))
      .catch(() => {});
  }, [setVoices]);

  useEffect(() => {
    if (location.pathname.includes('/voices/new')) {
      setShowModal(true);
    }
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      formData.append('file', file);

      const res = await apiClient.post('/voices/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      addVoice(res.data);
      setShowModal(false);
      setName('');
      setDescription('');
      setFile(null);
    } catch {
      alert("Failed to upload voice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Voices</h1>
          <p className="text-slate-400">Manage your cloned voices.</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-lg flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          Clone Voice
        </button>
      </div>

      {/* GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {voices.map((voice) => (
          <div key={voice.id}
            className="glass rounded-2xl p-5 relative overflow-hidden group cursor-pointer">
            
            {/* 🔥 BACKGROUND ICON */}
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
              <Mic2 className="w-24 h-24 text-blue-500" />
            </div>

            <div className="relative">
              <div className="p-3 bg-blue-500/10 rounded-xl w-fit">
                <Mic2 className="w-6 h-6 text-blue-400" />
              </div>

              <h3 className="mt-4 text-lg font-semibold text-white">
                {voice.name}
              </h3>

              <p className="text-sm text-slate-400">
                {voice.description || 'No description'}
              </p>
            </div>
          </div>
        ))}

        {voices.length === 0 && (
          <div className="col-span-full text-center py-12 border-2 border-dashed border-slate-800 rounded-2xl">
            <Mic2 className="mx-auto h-12 w-12 text-slate-600" />
            <p className="text-slate-400 mt-2">No voices yet</p>
          </div>
        )}
      </div>

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-white text-lg mb-4">Clone Voice</h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                value={name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
                placeholder="Voice name"
                className="w-full bg-slate-800 text-white p-2 rounded"
              />

              <textarea
                value={description}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
                placeholder="Description"
                className="w-full bg-slate-800 text-white p-2 rounded"
              />

              <input
                type="file"
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)}
              />

              <button className="w-full bg-blue-600 py-2 rounded">
                {loading ? "Uploading..." : "Upload"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Voices;
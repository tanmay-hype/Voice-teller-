import React, { useEffect, useState } from 'react';
import apiClient from '../services/apiClient';
import { useStoryStore } from '../store/storyStore';
import { BookOpen, Mic2, PlusCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { stories, voices, setStories, setVoices } = useStoryStore();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [storiesRes, voicesRes] = await Promise.all([
          apiClient.get('/stories/'),
          apiClient.get('/voices/'),
        ]);
        setStories(storiesRes.data);
        setVoices(voicesRes.data);
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      
      <div>
        <h1 className="text-3xl font-bold text-white">Overview</h1>
        <p className="text-slate-400 mt-2">Welcome to your AI Voice Storytelling platform.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-white text-xl flex items-center gap-2">
            <Mic2 /> Voices
          </h2>
          <p className="text-3xl text-white mt-4">{voices.length}</p>
          <Link to="/dashboard/voices" className="text-blue-400 mt-4 inline-block">
            Manage →
          </Link>
        </div>

        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-white text-xl flex items-center gap-2">
            <BookOpen /> Stories
          </h2>
          <p className="text-3xl text-white mt-4">{stories.length}</p>
          <Link to="/dashboard/stories" className="text-emerald-400 mt-4 inline-block">
            View →
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-white text-xl mb-4">Quick Actions</h2>
        <div className="flex gap-4">

          <button
            onClick={() => navigate('/dashboard/stories', { state: { openModal: true } })}
            className="px-5 py-3 bg-blue-600 text-white rounded-xl flex items-center"
          >
            <PlusCircle className="mr-2" />
            New Story
          </button>

          <button
            onClick={() => navigate('/dashboard/voices', { state: { openModal: true } })}
            className="px-5 py-3 bg-slate-800 text-white rounded-xl flex items-center"
          >
            <Mic2 className="mr-2" />
            Clone Voice
          </button>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
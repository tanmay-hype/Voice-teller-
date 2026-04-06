import React, { useEffect, useState } from 'react';
import apiClient from '../services/apiClient';
import { useStoryStore } from '../store/storyStore';
import { BookOpen, Mic2, PlusCircle, PlayCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { stories, voices, setStories, setVoices } = useStoryStore();
  const [loading, setLoading] = useState(true);

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
  }, [setStories, setVoices]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Overview</h1>
        <p className="mt-2 text-slate-400">Welcome to your AI Voice Storytelling platform.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Voices Stats Card */}
        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Mic2 className="w-24 h-24 text-blue-500" />
          </div>
          <div className="relative">
            <div className="flex items-center">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <Mic2 className="w-6 h-6 text-blue-400" />
              </div>
              <h2 className="ml-4 text-xl font-semibold text-white">Your Voices</h2>
            </div>
            <div className="mt-4">
              <span className="text-4xl font-bold text-white">{voices.length}</span>
              <span className="text-slate-400 ml-2">cloned voices</span>
            </div>
            <div className="mt-6 flex gap-3">
              <Link to="/dashboard/voices" className="text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors">Manage voices →</Link>
            </div>
          </div>
        </div>

        {/* Stories Stats Card */}
        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <BookOpen className="w-24 h-24 text-emerald-500" />
          </div>
          <div className="relative">
            <div className="flex items-center">
              <div className="p-3 bg-emerald-500/10 rounded-xl">
                <BookOpen className="w-6 h-6 text-emerald-400" />
              </div>
              <h2 className="ml-4 text-xl font-semibold text-white">Your Stories</h2>
            </div>
            <div className="mt-4">
              <span className="text-4xl font-bold text-white">{stories.length}</span>
              <span className="text-slate-400 ml-2">generated</span>
            </div>
            <div className="mt-6 flex gap-3">
              <Link to="/dashboard/stories" className="text-sm font-medium text-emerald-400 hover:text-emerald-300 transition-colors">View stories →</Link>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <Link to="/dashboard/stories/new" className="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-lg shadow-blue-600/20 font-medium transition-all flex items-center">
            <PlusCircle className="w-5 h-5 mr-2" />
            New Story
          </Link>
          <Link to="/dashboard/voices/new" className="px-5 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl shadow-lg font-medium transition-all flex items-center">
            <Mic2 className="w-5 h-5 mr-2" />
            Clone Voice
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

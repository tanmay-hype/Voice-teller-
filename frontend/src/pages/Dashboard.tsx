import React, { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import apiClient from '../services/apiClient';
import { useStoryStore } from '../store/storyStore';
import { BookOpen, Mic2, PlusCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const stories = useStoryStore((s) => s.stories);
  const voices = useStoryStore((s) => s.voices);
  const setStories = useStoryStore((s) => s.setStories);
  const setVoices = useStoryStore((s) => s.setVoices);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // fetch only counts for dashboard to avoid loading full payloads
        const [storiesCountRes, voicesCountRes] = await Promise.all([
          apiClient.get('/stories/count'),
          apiClient.get('/voices/count'),
        ]);
        setStories(new Array(storiesCountRes.data.count));
        setVoices(new Array(voicesCountRes.data.count));
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [setStories, setVoices]);

  const reduce = useReducedMotion();

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500/70 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: reduce ? 0 : 0.45 }}
      className="max-w-6xl mx-auto space-y-8"
    >
      <div>
        <h1 className="text-4xl font-bold text-[var(--text-strong)]">Overview</h1>
        <p className="text-[var(--text-muted)] mt-2">Welcome to your AI Voice Storytelling platform.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.995 }} className="card transition-shadow">
          <h2 className="text-[var(--text-strong)] text-xl flex items-center gap-2 font-semibold">
            <Mic2 className="text-[var(--accent)]" /> Voices
          </h2>
          <p className="text-4xl text-[var(--accent)] font-bold mt-4">{voices.length}</p>
          <Link to="/dashboard/voices" className="text-[var(--accent)] mt-4 inline-block font-medium hover:gap-2 flex items-center transition-all">
            Manage <span>→</span>
          </Link>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.995 }} className="card transition-shadow">
          <h2 className="text-[var(--text-strong)] text-xl flex items-center gap-2 font-semibold">
            <BookOpen className="text-[var(--accent)]" /> Stories
          </h2>
          <p className="text-4xl text-[var(--accent)] font-bold mt-4">{stories.length}</p>
          <Link to="/dashboard/stories" className="text-[var(--accent)] mt-4 inline-block font-medium hover:gap-2 flex items-center transition-all">
            View <span>→</span>
          </Link>
        </motion.div>
      </div>

      <div>
        <h2 className="text-[var(--text-strong)] text-xl mb-4 font-semibold">Quick Actions</h2>
        <div className="flex gap-4 flex-wrap">
          <motion.button
            onClick={() => navigate('/dashboard/stories', { state: { openModal: true } })}
            whileHover={{ y: -3 }}
            className="btn-primary flex items-center gap-2 hover:shadow-lg"
          >
            <PlusCircle className="w-4 h-4" />
            New Story
          </motion.button>

          <motion.button
            onClick={() => navigate('/dashboard/voices', { state: { openModal: true } })}
            whileHover={{ y: -2 }}
            className="btn-secondary flex items-center gap-2 hover:shadow-md"
          >
            <Mic2 className="w-4 h-4" />
            Clone Voice
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
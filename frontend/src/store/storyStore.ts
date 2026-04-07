import { create } from 'zustand';

/* =========================
   TYPES
========================= */

interface Story {
  id: string;
  title: string;
  content: string;
  audio_url?: string | null; // ✅ optional
  voice_id?: string | null;  // ✅ FIX (needed in Stories.tsx)
  created_at?: string;
}

interface Voice {
  id: string;
  name: string;
  description?: string; // ✅ optional
  elevenlabs_voice_id?: string; // ✅ FIX (needed in Voices.tsx)
}

/* =========================
   STORE STATE
========================= */

interface StoryState {
  stories: Story[];
  voices: Voice[];

  setStories: (stories: Story[]) => void;
  setVoices: (voices: Voice[]) => void;

  addStory: (story: Story) => void;
  addVoice: (voice: Voice) => void;

  clearStore: () => void; // ✅ useful for logout
}

/* =========================
   STORE
========================= */

export const useStoryStore = create<StoryState>((set) => ({
  stories: [],
  voices: [],

  setStories: (stories) => set({ stories }),

  setVoices: (voices) => set({ voices }),

  addStory: (story) =>
    set((state) => ({
      stories: [story, ...state.stories],
    })),

  addVoice: (voice) =>
    set((state) => ({
      voices: [voice, ...state.voices],
    })),

  clearStore: () =>
    set({
      stories: [],
      voices: [],
    }),
}));
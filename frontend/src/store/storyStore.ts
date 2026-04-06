import { create } from 'zustand';

interface Story {
  id: string;
  title: string;
  content: string;
  audio_url: string | null;
  created_at: string;
}

interface Voice {
  id: string;
  name: string;
  description: string;
}

interface StoryState {
  stories: Story[];
  voices: Voice[];
  setStories: (stories: Story[]) => void;
  setVoices: (voices: Voice[]) => void;
  addStory: (story: Story) => void;
  addVoice: (voice: Voice) => void;
}

export const useStoryStore = create<StoryState>()((set) => ({
  stories: [],
  voices: [],
  setStories: (stories) => set({ stories }),
  setVoices: (voices) => set({ voices }),
  addStory: (story) => set((state) => ({ stories: [story, ...state.stories] })),
  addVoice: (voice) => set((state) => ({ voices: [voice, ...state.voices] })),
}));

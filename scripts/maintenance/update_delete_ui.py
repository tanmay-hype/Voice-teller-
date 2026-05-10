#!/usr/bin/env python3
"""Update Stories.tsx with delete functionality"""

stories_file = r"c:\projects\ai-voice-storytelling\frontend\src\pages\Stories.tsx"

with open(stories_file, 'r') as f:
    content = f.read()

# Add Trash2 to imports
content = content.replace(
    "import { BookOpen, Plus } from 'lucide-react';",
    "import { BookOpen, Plus, Trash2 } from 'lucide-react';"
)

# Add handleDeleteStory function
handle_delete_fn = """
  const handleDeleteStory = async (storyId: string) => {
    if (!window.confirm('Are you sure you want to delete this story?')) return;
    
    try {
      await apiClient.delete(`/stories/${storyId}`);
      setStories(stories.filter((s: any) => s.id !== storyId));
      setSelectedStory(null);
    } catch (err) {
      alert('Failed to delete story');
    }
  };"""

# Find the handleSubmit function and add deleteStory after it
handleSubmit_end = "  };"
insertion_point = content.find("    }\n  };") + len("    }\n  };")
content = content[:insertion_point] + handle_delete_fn + content[insertion_point:]

# Add delete button to story cards
delete_btn_grid = """            {/* DELETE BUTTON */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteStory(story.id);
              }}
              className="absolute top-3 right-3 p-2 bg-red-600/80 hover:bg-red-700 rounded-lg transition"
              title="Delete story"
            >
              <Trash2 className="w-4 h-4 text-white" />
            </button>

            {/* 🔥 BACKGROUND ICON */}"""

content = content.replace(
    "            {/* 🔥 BACKGROUND ICON */}",
    delete_btn_grid,
    1
)

# Add delete button to modal view
delete_btn_modal = """              <button
                onClick={() => handleDeleteStory(selectedStory.id)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>

              <button onClick={() => setSelectedStory(null)} className="px-4 py-2 bg-slate-700 rounded">Close</button>"""

content = content.replace(
    '              <button onClick={() => setSelectedStory(null)} className="px-4 py-2 bg-slate-700 rounded">Close</button>',
    delete_btn_modal,
    1
)

with open(stories_file, 'w') as f:
    f.write(content)

print("✅ Updated Stories.tsx with delete functionality")

# Now update Voices.tsx
voices_file = r"c:\projects\ai-voice-storytelling\frontend\src\pages\Voices.tsx"

with open(voices_file, 'r') as f:
    content = f.read()

# Add Trash2 to imports
content = content.replace(
    "import { Mic2, Plus } from 'lucide-react';",
    "import { Mic2, Plus, Trash2 } from 'lucide-react';"
)

# Add handleDeleteVoice function
handle_delete_voice = """
  const handleDeleteVoice = async (voiceId: string) => {
    if (!window.confirm('Are you sure you want to delete this voice?')) return;
    
    try {
      await apiClient.delete(`/voices/${voiceId}`);
      setVoices(voices.filter((v: any) => v.id !== voiceId));
    } catch (err) {
      alert('Failed to delete voice');
    }
  };"""

# Insert after handleSubmit
handleSubmit_voices = content.find("    }\n  };")
if handleSubmit_voices > 0:
    insertion_point = handleSubmit_voices + len("    }\n  };")
    content = content[:insertion_point] + handle_delete_voice + content[insertion_point:]

# Add delete button to voice cards
delete_voice_btn = """            {/* DELETE BUTTON */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteVoice(voice.id);
              }}
              className="absolute top-3 right-3 p-2 bg-red-600/80 hover:bg-red-700 rounded-lg transition"
              title="Delete voice"
            >
              <Trash2 className="w-4 h-4 text-white" />
            </button>

            {/* 🔥 BACKGROUND ICON */}"""

content = content.replace(
    "            {/* 🔥 BACKGROUND ICON */}",
    delete_voice_btn,
    1
)

with open(voices_file, 'w') as f:
    f.write(content)

print("✅ Updated Voices.tsx with delete functionality")

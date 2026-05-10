# Script to update Stories.tsx with delete functionality
$storiesFile = "c:\projects\ai-voice-storytelling\frontend\src\pages\Stories.tsx"
$content = Get-Content $storiesFile -Raw

# Update import to include Trash2
$content = $content -replace "import { BookOpen, Plus } from 'lucide-react';", "import { BookOpen, Plus, Trash2 } from 'lucide-react';"

# Add handleDeleteStory function after handleSubmit
$handleDeleteStoryFn = @'
  
  const handleDeleteStory = async (storyId: string) => {
    if (!window.confirm('Are you sure you want to delete this story?')) return;
    
    try {
      await apiClient.delete(`/stories/${ storyId }`);
      setStories(stories.filter((s: any) => s.id !== storyId));
      setSelectedStory(null);
    } catch (err) {
      alert('Failed to delete story');
    }
  };
'@

$content = $content -replace "(\s+}\s+}\);", $handleDeleteStoryFn + "`n`n    };" -replace "`$1", "  }`n`n" + $handleDeleteStoryFn

# Add delete button to grid items (after render)
$deleteButtonInGrid = @"
            {/* DELETE BUTTON */}
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

            {/* 🔥 BACKGROUND ICON */}
"@

$content = $content -replace "(\s+{/\* 🔥 BACKGROUND ICON \*/)", $deleteButtonInGrid

# Add delete button to modal
$deleteButtonInModal = @"
              <button
                onClick={() => handleDeleteStory(selectedStory.id)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>

              <button onClick={() => setSelectedStory(null)} className="px-4 py-2 bg-slate-700 rounded">Close</button>
"@

$content = $content -replace "(<button onClick=\{\(\) => setSelectedStory\(null\)\} className=""px-4 py-2 bg-slate-700 rounded"">Close</button>)", $deleteButtonInModal

Set-Content -Path $storiesFile -Value $content -Force
Write-Host "✅ Updated Stories.tsx with delete functionality"

import { Spinner } from "@radix-ui/themes"
import { useEffect, useState } from "react"
import { AppTemplate } from "./AppTemplate"
import CreateStory from "./CreateStory"
import StoryPlayer from "./StoryPlayer"
import StoryVisualizer from "./StoryVisualizer"
import { createStory, getStory, type Story } from "./api"

export default function App() {
    const [story, setStory] = useState<Story | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [autoplay, setAutoplay] = useState(false)
    const [isVisualizing, setIsVisualizing] = useState(false)

    useEffect(() => {
        const path = window.location.pathname
        const storyIdMatch = path.match(/^\/story\/(.+)$/)
        const visualizeMatch = path.match(/^\/visualize\/(.+)$/)

        if (storyIdMatch) {
            const storyId = storyIdMatch[1]
            loadStory(storyId)
        } else if (visualizeMatch) {
            const storyId = visualizeMatch[1]
            loadStory(storyId)
            setIsVisualizing(true)
        }
    }, [])

    const loadStory = async (storyId: string) => {
        setIsLoading(true)
        try {
            const loadedStory = await getStory(storyId)
            setStory(loadedStory)
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreateStory = async (prompt: string) => {
        setIsLoading(true)
        try {
            const { story } = await createStory(prompt)
            setStory(story)
            setAutoplay(true)
            window.history.pushState(null, "", `/story/${story.id}`)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <AppTemplate>
            {isLoading ? (
                <Spinner size="3" />
            ) : story ? (
                isVisualizing ? (
                    <StoryVisualizer story={story} />
                ) : (
                    // We disable auto continue for demos to make it more interactive!
                    <StoryPlayer story={story} autoplay={autoplay} autoContinue={false} />
                )
            ) : (
                <CreateStory onCreateStory={handleCreateStory} />
            )}
        </AppTemplate>
    )
}

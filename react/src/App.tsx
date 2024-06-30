import { ReaderIcon } from "@radix-ui/react-icons"
import { AlertDialog, Box, Card, Container, Flex, Spinner, Text, Theme } from "@radix-ui/themes"
import { useEffect, useState } from "react"
import CreateStory from "./CreateStory"
import StoryPlayer from "./StoryPlayer"
import StoryVisualizer from "./StoryVisualizer"
import { createStory, getStory, type Story } from "./api"
import { useIsDarkMode } from "./useIsDarkMode"

export default function App() {
    const isDarkMode = useIsDarkMode()
    const [story, setStory] = useState<Story | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
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
        setError(null)
        try {
            const loadedStory = await getStory(storyId)
            setStory(loadedStory)
        } catch (error) {
            console.error("Error loading story:", error)
            setError("Failed to load story. Please try again.")
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreateStory = async (prompt: string) => {
        setIsLoading(true)
        setError(null)
        try {
            const newStory = await createStory(prompt)
            setStory(newStory)
            setAutoplay(true)
            window.history.pushState(null, "", `/story/${newStory.id}`)
        } catch (error) {
            console.error("Error creating story:", error)
            setError("Failed to create story. Please try again.")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Theme appearance={isDarkMode ? "dark" : "light"}>
            <Container p="2" minHeight="100vh">
                <Flex direction="column" height="100vh">
                    <Box width="100%">
                        <Card>
                            <Flex align="center" gap="2">
                                <ReaderIcon />
                                <Text weight="bold">PocketPal</Text>
                            </Flex>
                        </Card>
                    </Box>
                    <Flex direction="column" align="center" justify="center" flexGrow="1">
                        {isLoading ? (
                            <Spinner size="3" />
                        ) : error ? (
                            <AlertDialog.Root open={!!error}>
                                <AlertDialog.Content>
                                    <AlertDialog.Title>Error</AlertDialog.Title>
                                    <AlertDialog.Description>{error}</AlertDialog.Description>
                                    <Flex justify="end">
                                        <AlertDialog.Action onClick={() => setError(null)}>Close</AlertDialog.Action>
                                    </Flex>
                                </AlertDialog.Content>
                            </AlertDialog.Root>
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
                    </Flex>
                </Flex>
            </Container>
        </Theme>
    )
}

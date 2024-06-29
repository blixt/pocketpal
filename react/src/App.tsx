import { ReaderIcon } from "@radix-ui/react-icons"
import { Box, Card, Container, Flex, Text, Theme } from "@radix-ui/themes"
import { useState } from "react"
import CreateStory from "./CreateStory"
import Story from "./Story"
import { useIsDarkMode } from "./useIsDarkMode"

export default function App() {
    const isDarkMode = useIsDarkMode()
    const [story, setStory] = useState<{ title: string; currentBranch: string } | null>(null)

    const handleCreateStory = (prompt: string) => {
        // Create a temporary story with dummy data
        setStory({
            title: prompt.slice(0, 30), // Use first 30 characters of prompt as title
            currentBranch: `temp-${Math.random().toString(36).substring(2, 9)}`, // Generate a random branch ID
        })
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
                        {story ? (
                            <Story story={story} currentBranch={story.currentBranch} />
                        ) : (
                            <CreateStory onCreateStory={handleCreateStory} />
                        )}
                    </Flex>
                </Flex>
            </Container>
        </Theme>
    )
}

import { Box, Button, Card, Heading, TextArea } from "@radix-ui/themes"
import { useState, type KeyboardEvent } from "react"

interface CreateStoryProps {
    onCreateStory: (prompt: string) => void
}

export default function CreateStory({ onCreateStory }: CreateStoryProps) {
    const [prompt, setPrompt] = useState("")
    const [isCreatingStory, setIsCreatingStory] = useState(false)

    const handlePromptChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setPrompt(event.target.value)
    }

    const handleStartStory = () => {
        if (isCreatingStory) return
        setIsCreatingStory(true)
        onCreateStory(prompt)
    }

    const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
        if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
            handleStartStory()
        }
    }

    return (
        <Box maxWidth="400px" width="100%">
            <Card>
                <Heading size="6" mb="4">
                    Begin your story
                </Heading>
                <TextArea
                    placeholder="Enter the seed of your story here..."
                    value={prompt}
                    onChange={handlePromptChange}
                    onKeyDown={handleKeyDown}
                    mb="4"
                    disabled={isCreatingStory}
                />
                <Button onClick={handleStartStory} disabled={isCreatingStory}>
                    Start this journey
                </Button>
            </Card>
        </Box>
    )
}

import { Box, Button, Card, Heading, TextArea } from "@radix-ui/themes"
import { useState } from "react"

interface CreateStoryProps {
    onCreateStory: (prompt: string) => void
}

export default function CreateStory({ onCreateStory }: CreateStoryProps) {
    const [prompt, setPrompt] = useState("")

    const handlePromptChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setPrompt(event.target.value)
    }

    const handleStartStory = () => {
        onCreateStory(prompt)
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
                    mb="4"
                />
                <Button onClick={handleStartStory}>Start this journey</Button>
            </Card>
        </Box>
    )
}

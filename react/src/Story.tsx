import { Button, Flex, Heading } from "@radix-ui/themes"
import { useState } from "react"

interface StoryProps {
    story: {
        title: string
        // Add other story properties as needed
    }
    currentBranch: string
}

export default function Story({ story }: StoryProps) {
    const [sentiment, setSentiment] = useState<"positive" | "negative" | null>(null)

    const handleSentimentChange = (value: "positive" | "negative") => {
        setSentiment(prevSentiment => (prevSentiment === value ? null : value))
    }

    return (
        <Flex direction="column" align="center">
            <Heading size="6" mb="4">
                {story.title}
            </Heading>
            <Flex direction="column" gap="4">
                <Button
                    size="4"
                    onClick={() => handleSentimentChange("positive")}
                    style={{ width: "200px", height: "200px", fontSize: "100px" }}
                    variant={sentiment === "positive" ? "solid" : "soft"}
                >
                    +
                </Button>
                <Button
                    size="4"
                    onClick={() => handleSentimentChange("negative")}
                    style={{ width: "200px", height: "200px", fontSize: "100px" }}
                    variant={sentiment === "negative" ? "solid" : "soft"}
                >
                    -
                </Button>
            </Flex>
        </Flex>
    )
}

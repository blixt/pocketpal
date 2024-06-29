import { Box, Card, Flex, Heading, Text, Theme } from "@radix-ui/themes"
import { useIsDarkMode } from "./useIsDarkMode"

export default function App() {
    const isDarkMode = useIsDarkMode()
    return (
        <Theme appearance={isDarkMode ? "dark" : "light"}>
            <Flex align="center" justify="center" height="100vh">
                <Box maxWidth="400px">
                    <Card>
                        <Heading size="6">PocketPal</Heading>
                        <Text>Under construction. Coming soon!</Text>
                    </Card>
                </Box>
            </Flex>
        </Theme>
    )
}

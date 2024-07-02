import { ReaderIcon } from "@radix-ui/react-icons"
import { Box, Card, Container, Flex, Text, Theme } from "@radix-ui/themes"
import { useIsDarkMode } from "./useIsDarkMode"

export function AppTemplate({ children }: { children: React.ReactNode }) {
    const isDarkMode = useIsDarkMode()
    return (
        <Theme appearance={isDarkMode ? "dark" : "light"}>
            <Container p="4" minHeight="100vh">
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
                        {children}
                    </Flex>
                </Flex>
            </Container>
        </Theme>
    )
}

import { AlertDialog, Flex } from "@radix-ui/themes"
import "@radix-ui/themes/styles.css"
import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App.tsx"
import { AppTemplate } from "./AppTemplate.tsx"
import "./index.css"

interface ErrorBoundaryProps {
    children: React.ReactNode
}

interface ErrorBoundaryState {
    error: Error | null
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    state: ErrorBoundaryState = { error: null }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { error }
    }

    render() {
        if (this.state.error) {
            return (
                <AppTemplate>
                    <AlertDialog.Root open={true}>
                        <AlertDialog.Content>
                            <AlertDialog.Title>Error</AlertDialog.Title>
                            <AlertDialog.Description>{this.state.error.message}</AlertDialog.Description>
                            <Flex justify="end">
                                <AlertDialog.Action
                                    onClick={() => {
                                        window.location.reload()
                                    }}
                                >
                                    Reload
                                </AlertDialog.Action>
                            </Flex>
                        </AlertDialog.Content>
                    </AlertDialog.Root>
                </AppTemplate>
            )
        }

        return this.props.children
    }
}

const rootEl = document.getElementById("root")
if (!rootEl) throw Error("missing #root")

const root = createRoot(rootEl)
root.render(
    <React.StrictMode>
        <ErrorBoundary>
            <App />
        </ErrorBoundary>
    </React.StrictMode>,
)

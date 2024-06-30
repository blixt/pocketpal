import { PlayIcon } from "@radix-ui/react-icons"
import { Button, Flex, Heading } from "@radix-ui/themes"
import { useEffect, useReducer, useRef } from "react"
import { generateBranch, getBranch, type Branch, type Story } from "./api"

interface StoryProps {
    autoplay?: boolean
    story: Story
}

type State = {
    currentBranch: Branch | null
    upcomingBranch: Branch | null
    sentiment: "positive" | "negative" | null
    isButtonsDisabled: boolean
    hasAudioEnded: boolean
    isPlaying: boolean
}

type Action =
    | { type: "SET_INITIAL_BRANCH"; branch: Branch }
    | { type: "SET_UPCOMING_BRANCH"; branch: Branch }
    | { type: "SET_SENTIMENT"; sentiment: "positive" | "negative" | null }
    | { type: "DISABLE_BUTTONS" }
    | { type: "AUDIO_ENDED" }
    | { type: "TRANSITION_TO_NEXT_BRANCH" }
    | { type: "START_PLAYING" }

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "SET_INITIAL_BRANCH":
            if (state.currentBranch) {
                throw new Error("Cannot set initial branch: current branch is not null")
            }
            return { ...state, currentBranch: action.branch }
        case "SET_UPCOMING_BRANCH":
            return { ...state, upcomingBranch: action.branch }
        case "SET_SENTIMENT":
            return { ...state, sentiment: action.sentiment }
        case "DISABLE_BUTTONS":
            return { ...state, isButtonsDisabled: true }
        case "AUDIO_ENDED":
            return { ...state, hasAudioEnded: true }
        case "TRANSITION_TO_NEXT_BRANCH":
            if (!state.upcomingBranch) {
                throw new Error("Cannot transition to next branch: upcoming branch is null")
            }
            return {
                ...state,
                currentBranch: state.upcomingBranch,
                upcomingBranch: null,
                sentiment: null,
                isButtonsDisabled: false,
                hasAudioEnded: false,
            }
        case "START_PLAYING":
            return { ...state, isPlaying: true }
        default:
            throw new Error("Unexpected action type")
    }
}

function withLogging(reducer: (state: State, action: Action) => State) {
    return (state: State, action: Action) => {
        console.log("Previous state:", state)
        console.log("Action:", action)
        const nextState = reducer(state, action)
        console.log("Next state:", nextState)
        return nextState
    }
}

export default function StoryPlayer({ story, autoplay = false }: StoryProps) {
    const [state, dispatch] = useReducer(withLogging(reducer), {
        currentBranch: null,
        upcomingBranch: null,
        sentiment: null,
        isButtonsDisabled: false,
        hasAudioEnded: false,
        isPlaying: autoplay,
    })

    const audioRef = useRef<HTMLAudioElement | null>(null)

    const didRunFetchInitialBranch = useRef(false)
    useEffect(() => {
        if (didRunFetchInitialBranch.current) return
        didRunFetchInitialBranch.current = true
        const fetchInitialBranch = async () => {
            try {
                const branch = await getBranch(story.id, story.initial_branch_id)
                dispatch({ type: "SET_INITIAL_BRANCH", branch: branch })
            } catch (error) {
                console.error("Error fetching initial branch:", error)
            }
        }
        fetchInitialBranch()
    }, [story.id, story.initial_branch_id])

    useEffect(() => {
        if (!state.currentBranch || !state.isPlaying) return
        const audio = audioRef.current
        if (!audio) return

        audio.src = state.currentBranch.audio_url
        audio.currentTime = 0
        audio.play().catch(error => console.error("Error playing audio:", error))
    }, [state.currentBranch, state.isPlaying])

    useEffect(() => {
        if (!state.currentBranch) return
        const currentBranch = state.currentBranch

        const fetchUpcomingBranch = async () => {
            const branchId =
                state.sentiment === "negative" ? currentBranch.negative_branch_id : currentBranch.positive_branch_id

            if (!branchId) return

            try {
                const branch = await getBranch(currentBranch.story_id, branchId)
                dispatch({ type: "SET_UPCOMING_BRANCH", branch: branch })
                if (state.hasAudioEnded) {
                    dispatch({ type: "TRANSITION_TO_NEXT_BRANCH" })
                }
            } catch (error) {
                console.error("Error fetching upcoming branch:", error)
            }
        }

        fetchUpcomingBranch()
    }, [state.currentBranch, state.sentiment, state.hasAudioEnded])

    useEffect(() => {
        const audio = audioRef.current
        if (!audio) return

        // If the audio is nearing the end, lock in the user's choice.
        const checkTimeRemaining = () => {
            if (audio.paused) return
            const timeRemaining = audio.duration - audio.currentTime
            if (timeRemaining >= 3) {
                setTimeout(checkTimeRemaining, 100)
                return
            }

            dispatch({ type: "DISABLE_BUTTONS" })
            if (state.sentiment === null) {
                handleSentimentChange("positive")
            }
        }

        const handleAudioEnd = () => {
            dispatch({ type: "AUDIO_ENDED" })
            if (!state.upcomingBranch) return
            dispatch({ type: "TRANSITION_TO_NEXT_BRANCH" })
        }

        const timeoutId = setTimeout(checkTimeRemaining, 100)
        audio.addEventListener("ended", handleAudioEnd)

        return () => {
            clearTimeout(timeoutId)
            audio.removeEventListener("ended", handleAudioEnd)
        }
    }, [state.sentiment, state.upcomingBranch])

    const handleSentimentChange = async (sentiment: "positive" | "negative") => {
        if (state.isButtonsDisabled) return

        dispatch({ type: "SET_SENTIMENT", sentiment: state.sentiment === sentiment ? null : sentiment })
        if (state.currentBranch) {
            try {
                const newBranch = await generateBranch(state.currentBranch.story_id, state.currentBranch.id, sentiment)
                dispatch({ type: "SET_UPCOMING_BRANCH", branch: newBranch })
                if (state.hasAudioEnded) {
                    dispatch({ type: "TRANSITION_TO_NEXT_BRANCH" })
                }
            } catch (error) {
                console.error("Error generating new branch:", error)
            }
        }
    }

    const handlePlayClick = () => {
        dispatch({ type: "START_PLAYING" })
    }

    return (
        <Flex direction="column" align="center">
            <Heading size="6" mb="4">
                {story.title}
            </Heading>
            {/* biome-ignore lint/a11y/useMediaCaption: Not for now. */}
            <audio ref={audioRef} style={{ display: "none" }} />
            <Flex direction="column" gap="4">
                {state.isPlaying ? (
                    <>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("positive")}
                            style={{ width: "200px", height: "200px", fontSize: "100px" }}
                            variant={state.sentiment === "positive" ? "solid" : "soft"}
                            disabled={state.isButtonsDisabled}
                        >
                            +
                        </Button>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("negative")}
                            style={{ width: "200px", height: "200px", fontSize: "100px" }}
                            variant={state.sentiment === "negative" ? "solid" : "soft"}
                            disabled={state.isButtonsDisabled}
                        >
                            -
                        </Button>
                    </>
                ) : (
                    <Button
                        size="4"
                        onClick={handlePlayClick}
                        style={{ width: "200px", height: "200px" }}
                        disabled={!state.currentBranch || state.isPlaying}
                    >
                        <PlayIcon width="100" height="100" />
                    </Button>
                )}
            </Flex>
        </Flex>
    )
}

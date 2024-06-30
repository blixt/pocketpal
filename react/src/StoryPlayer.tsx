import { MinusIcon, PlayIcon, PlusIcon } from "@radix-ui/react-icons"
import { Button, Flex, Heading, Text } from "@radix-ui/themes"
import { useEffect, useReducer, useRef } from "react"
import { getBranch, type Branch, type Story } from "./api"
import toneSrc from "./audio/tone.mp3"

interface StoryProps {
    autoplay?: boolean
    story: Story
    autoContinue?: boolean
}

type State = {
    currentBranch: Branch | null
    upcomingBranch: Branch | null
    sentiment: "positive" | "negative" | null
    hasAudioEnded: boolean
    isPlaying: boolean
}

type Action =
    | { type: "SET_INITIAL_BRANCH"; branch: Branch }
    | { type: "SET_UPCOMING_BRANCH"; branch: Branch }
    | { type: "SET_SENTIMENT"; sentiment: "positive" | "negative" | null }
    | { type: "AUDIO_ENDED" }
    | { type: "AUDIO_PAUSED" }
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
        case "AUDIO_ENDED":
            // Make sure to force isPlaying to be true if audio ends. While it
            // may seem counter-intuitive, audio ending means it was playing,
            // and should keep playing once the next audio loads. Otherwise, the
            // pause event that happens when audio ends might stop the flow.
            return { ...state, hasAudioEnded: true, isPlaying: true }
        case "TRANSITION_TO_NEXT_BRANCH":
            if (!state.upcomingBranch) {
                throw new Error("Cannot transition to next branch: upcoming branch is null")
            }
            return {
                ...state,
                currentBranch: state.upcomingBranch,
                upcomingBranch: null,
                sentiment: null,
                hasAudioEnded: false,
            }
        case "START_PLAYING":
            return { ...state, isPlaying: true }
        case "AUDIO_PAUSED":
            // If the audio has ended, then this pause event was probably not
            // because of a user action, so we ignore it.
            if (state.hasAudioEnded) return state
            return { ...state, isPlaying: false }
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

export default function StoryPlayer({ story, autoplay = false, autoContinue = true }: StoryProps) {
    const [state, dispatch] = useReducer(withLogging(reducer), {
        currentBranch: null,
        upcomingBranch: null,
        sentiment: null,
        hasAudioEnded: false,
        isPlaying: autoplay,
    })

    const audioRef = useRef<HTMLAudioElement | null>(null)
    const toneAudioRef = useRef<HTMLAudioElement | null>(null)

    const didRunFetchInitialBranch = useRef(false)
    useEffect(() => {
        if (didRunFetchInitialBranch.current) return
        didRunFetchInitialBranch.current = true
        const fetchInitialBranch = async () => {
            try {
                const branch = await getBranch(story.id, story.initial_branch_id)
                dispatch({ type: "SET_INITIAL_BRANCH", branch })
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
        const toneAudio = toneAudioRef.current
        if (!audio || !toneAudio) return

        // If the audio is nearing the end, lock in the user's choice.
        const checkTimeRemaining = () => {
            if (audio.paused || !audio.duration) return
            const timeRemaining = audio.duration - audio.currentTime
            if (timeRemaining >= 2) {
                setTimeout(checkTimeRemaining, 100)
                return
            }

            if (autoContinue && state.sentiment === null) {
                handleSentimentChange("positive")
            }
        }

        const handleAudioEnd = () => {
            dispatch({ type: "AUDIO_ENDED" })
            if (!autoContinue) {
                toneAudio.play().catch(error => console.error("Error playing tone audio:", error))
            }
            if (!state.upcomingBranch) return
            dispatch({ type: "TRANSITION_TO_NEXT_BRANCH" })
        }

        const handleAudioPause = () => {
            dispatch({ type: "AUDIO_PAUSED" })
        }

        const timeoutId = setTimeout(checkTimeRemaining, 100)
        audio.addEventListener("ended", handleAudioEnd)
        audio.addEventListener("pause", handleAudioPause)

        return () => {
            clearTimeout(timeoutId)
            audio.removeEventListener("ended", handleAudioEnd)
            audio.removeEventListener("pause", handleAudioPause)
        }
    }, [state.sentiment, state.upcomingBranch, autoContinue])

    const handleSentimentChange = async (sentiment: "positive" | "negative") => {
        dispatch({ type: "SET_SENTIMENT", sentiment: state.sentiment === sentiment ? null : sentiment })
        if (state.currentBranch) {
            try {
                // Refetch the current branch data
                const updatedBranch = await getBranch(state.currentBranch.story_id, state.currentBranch.id)

                // Check if the appropriate branch ID is available
                const nextBranchId =
                    sentiment === "positive" ? updatedBranch.positive_branch_id : updatedBranch.negative_branch_id

                if (nextBranchId) {
                    // Fetch the next branch if available
                    const nextBranch = await getBranch(state.currentBranch.story_id, nextBranchId)
                    dispatch({ type: "SET_UPCOMING_BRANCH", branch: nextBranch })

                    if (state.hasAudioEnded) {
                        dispatch({ type: "TRANSITION_TO_NEXT_BRANCH" })
                    }
                } else {
                    console.warn(`No ${sentiment} branch available for the current branch.`)
                }
            } catch (error) {
                console.error("Error fetching updated branch data:", error)
            }
        }
    }

    const handlePlayClick = () => {
        dispatch({ type: "START_PLAYING" })
    }

    return (
        <Flex direction="column" gap="4" align="center">
            <Heading size="6">{story.title}</Heading>
            <Text>{story.description}</Text>
            <Flex direction="column" gap="4">
                {state.isPlaying ? (
                    <>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("positive")}
                            style={{ width: "200px", height: "200px", fontSize: "100px" }}
                            variant={state.sentiment === "positive" ? "solid" : "outline"}
                            color="green"
                        >
                            <PlusIcon width="100" height="100" />
                        </Button>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("negative")}
                            style={{ width: "200px", height: "200px", fontSize: "100px" }}
                            variant={state.sentiment === "negative" ? "solid" : "outline"}
                            color="red"
                        >
                            <MinusIcon width="100" height="100" />
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
            {/* biome-ignore lint/a11y/useMediaCaption: Not for now. */}
            <audio ref={audioRef} style={{ display: "none" }} />
            {/* biome-ignore lint/a11y/useMediaCaption: Not for now. */}
            <audio ref={toneAudioRef} src={toneSrc} style={{ display: "none" }} />
        </Flex>
    )
}

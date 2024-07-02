import {
    LightningBoltIcon,
    MinusIcon,
    PauseIcon,
    PlayIcon,
    PlusIcon,
    ReloadIcon,
    TimerIcon,
    TrackPreviousIcon,
} from "@radix-ui/react-icons"
import { Button, Flex, Heading, IconButton, Text } from "@radix-ui/themes"
import { useEffect, useReducer, useRef, useState } from "react"
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
    playbackRate: number
    previousBranches: Branch[]
}

type Action =
    | { type: "SET_INITIAL_BRANCH"; branch: Branch }
    | { type: "SET_UPCOMING_BRANCH"; branch: Branch; fromBranchId: string }
    | { type: "SET_SENTIMENT"; sentiment: "positive" | "negative" | null }
    | { type: "AUDIO_ENDED" }
    | { type: "AUDIO_PAUSED" }
    | { type: "AUDIO_PLAYED" }
    | { type: "TRANSITION_TO_NEXT_BRANCH"; fromBranchId: string }
    | { type: "TOGGLE_PLAYING" }
    | { type: "TOGGLE_PLAYBACK_SPEED" }
    | { type: "GO_BACK" }

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "SET_INITIAL_BRANCH":
            if (state.currentBranch) {
                throw new Error("Cannot set initial branch: current branch is not null")
            }
            return { ...state, currentBranch: action.branch }
        case "SET_UPCOMING_BRANCH":
            if (state.currentBranch?.id !== action.fromBranchId) {
                console.warn(
                    `Cannot set upcoming branch: fromBranchId (${action.fromBranchId}) does not match currentBranch.id (${state.currentBranch?.id})`,
                )
                return state
            }
            return { ...state, upcomingBranch: action.branch }
        case "SET_SENTIMENT": {
            const newState: State = { ...state, sentiment: action.sentiment }
            if (!newState.hasAudioEnded) {
                newState.isPlaying = true
            }
            return newState
        }
        case "AUDIO_ENDED":
            return { ...state, hasAudioEnded: true }
        case "TRANSITION_TO_NEXT_BRANCH":
            if (state.currentBranch?.id !== action.fromBranchId) {
                console.warn(
                    `Cannot transition to next branch: fromBranchId (${action.fromBranchId}) does not match currentBranch.id (${state.currentBranch?.id})`,
                )
                return state
            }
            if (state.currentBranch.id === state.upcomingBranch?.id) {
                throw new Error("Cannot transition to next branch: current and upcoming branch are the same")
            }
            if (!state.upcomingBranch) {
                throw new Error("Cannot transition to next branch: upcoming branch is null")
            }
            if (!state.sentiment) {
                throw new Error("Cannot transition to next branch: sentiment is not set")
            }
            return {
                ...state,
                currentBranch: state.upcomingBranch,
                upcomingBranch: null,
                sentiment: null,
                hasAudioEnded: false,
                isPlaying: true,
                previousBranches: [...state.previousBranches, state.currentBranch],
            }
        case "TOGGLE_PLAYING":
            return { ...state, isPlaying: !state.isPlaying }
        case "AUDIO_PAUSED":
            return { ...state, isPlaying: false }
        case "AUDIO_PLAYED":
            return { ...state, isPlaying: true }
        case "TOGGLE_PLAYBACK_SPEED":
            return { ...state, playbackRate: state.playbackRate === 1 ? 2 : 1 }
        case "GO_BACK": {
            if (state.previousBranches.length === 0) {
                return state
            }
            const previousBranch = state.previousBranches[state.previousBranches.length - 1]
            return {
                ...state,
                currentBranch: previousBranch,
                upcomingBranch: null,
                sentiment: null,
                hasAudioEnded: false,
                isPlaying: true,
                previousBranches: state.previousBranches.slice(0, -1),
            }
        }
        default:
            throw new Error("Unexpected action type")
    }
}

function withLogging(reducer: (state: State, action: Action) => State) {
    return (state: State, action: Action) => {
        const nextState = reducer(state, action)
        console.log({ previousState: state, nextState, action })
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
        playbackRate: 1,
        previousBranches: [],
    })

    const [canPlay, setCanPlay] = useState(false)

    const audioRef = useRef<HTMLAudioElement | null>(null)
    const toneAudioRef = useRef<HTMLAudioElement | null>(null)

    // Preload tone.mp3 as soon as possible
    useEffect(() => {
        const toneAudio = new Audio(toneSrc)
        toneAudio.preload = "auto"
        toneAudioRef.current = toneAudio
    }, [])

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
        if (!state.currentBranch) return
        const audio = audioRef.current
        if (!audio) return

        if (state.currentBranch.audio_url !== audio.src) {
            audio.src = state.currentBranch.audio_url
            audio.load()
        }

        audio.playbackRate = state.playbackRate

        if (state.isPlaying) {
            audio.play().catch(error => console.error("Error playing audio:", error))
        } else {
            audio.pause()
        }
    }, [state.currentBranch, state.isPlaying, state.playbackRate])

    useEffect(() => {
        if (!state.currentBranch || !state.sentiment) return
        const currentBranch = state.currentBranch

        const fetchUpcomingBranch = async () => {
            const branchId =
                state.sentiment === "negative" ? currentBranch.negative_branch_id : currentBranch.positive_branch_id

            if (!branchId) return

            try {
                const branch = await getBranch(currentBranch.story_id, branchId)
                dispatch({ type: "SET_UPCOMING_BRANCH", branch: branch, fromBranchId: currentBranch.id })
                if (state.hasAudioEnded && state.sentiment) {
                    dispatch({ type: "TRANSITION_TO_NEXT_BRANCH", fromBranchId: currentBranch.id })
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

        const checkTimeRemaining = () => {
            if (audio.paused || !audio.duration) return
            const timeRemaining = audio.duration - audio.currentTime
            if (timeRemaining >= 3) {
                setTimeout(checkTimeRemaining, 100)
                return
            }
            if (state.sentiment !== null) {
                // The user already made a choice.
                return
            }
            if (autoContinue) {
                // Automatically pick positive for the user.
                handleSentimentChange("positive")
                preloadUpcomingBranches(state.currentBranch, "positive")
            } else {
                // Preload both options so that whichever option the user picks, it plays sooner.
                preloadUpcomingBranches(state.currentBranch)
            }
        }

        const handleAudioEnd = () => {
            dispatch({ type: "AUDIO_ENDED" })
            if (state.sentiment === null) {
                toneAudioRef.current?.play().catch(error => console.error("Error playing tone audio:", error))
            } else if (state.upcomingBranch && state.sentiment && state.currentBranch) {
                dispatch({ type: "TRANSITION_TO_NEXT_BRANCH", fromBranchId: state.currentBranch.id })
            }
        }

        const handleAudioPause = () => {
            dispatch({ type: "AUDIO_PAUSED" })
        }

        const handleAudioPlay = () => {
            dispatch({ type: "AUDIO_PLAYED" })
        }

        const handleCanPlay = () => {
            setCanPlay(true)
        }

        const handleWaiting = () => {
            setCanPlay(false)
        }

        const timeoutId = setTimeout(checkTimeRemaining, 100)
        audio.addEventListener("ended", handleAudioEnd)
        audio.addEventListener("pause", handleAudioPause)
        audio.addEventListener("play", handleAudioPlay)
        audio.addEventListener("canplay", handleCanPlay)
        audio.addEventListener("waiting", handleWaiting)

        return () => {
            clearTimeout(timeoutId)
            audio.removeEventListener("ended", handleAudioEnd)
            audio.removeEventListener("pause", handleAudioPause)
            audio.removeEventListener("play", handleAudioPlay)
            audio.removeEventListener("canplay", handleCanPlay)
            audio.removeEventListener("waiting", handleWaiting)
        }
    }, [state.sentiment, state.upcomingBranch, autoContinue, state.currentBranch])

    const handleSentimentChange = async (sentiment: "positive" | "negative") => {
        dispatch({ type: "SET_SENTIMENT", sentiment: state.sentiment === sentiment ? null : sentiment })
        if (!state.currentBranch) return
        try {
            const nextBranchId =
                sentiment === "positive"
                    ? state.currentBranch.positive_branch_id
                    : state.currentBranch.negative_branch_id

            if (!nextBranchId) {
                console.warn(`No ${sentiment} branch available for the current branch.`)
                return
            }

            if (state.upcomingBranch?.id !== nextBranchId) {
                const nextBranch = await getBranch(state.currentBranch.story_id, nextBranchId)
                dispatch({ type: "SET_UPCOMING_BRANCH", branch: nextBranch, fromBranchId: state.currentBranch.id })
            }

            if (state.hasAudioEnded) {
                dispatch({ type: "TRANSITION_TO_NEXT_BRANCH", fromBranchId: state.currentBranch.id })
            }
        } catch (error) {
            console.error("Error fetching updated branch data:", error)
        }
    }

    const handlePlayPauseClick = () => {
        dispatch({ type: "TOGGLE_PLAYING" })
    }

    const handlePlaybackSpeedClick = () => {
        dispatch({ type: "TOGGLE_PLAYBACK_SPEED" })
    }

    const handleReload = () => {
        window.location.reload()
    }

    const handleGoBack = () => {
        dispatch({ type: "GO_BACK" })
    }

    return (
        <Flex direction="column" gap="4" align="center">
            <Flex direction="row" gap="2">
                <IconButton
                    size="4"
                    variant="classic"
                    radius="full"
                    onClick={handleGoBack}
                    disabled={state.previousBranches.length === 0}
                >
                    <TrackPreviousIcon width="24" height="24" />
                </IconButton>
                <IconButton size="4" variant="classic" radius="full" onClick={handlePlayPauseClick} loading={!canPlay}>
                    {state.isPlaying ? <PauseIcon width="24" height="24" /> : <PlayIcon width="24" height="24" />}
                </IconButton>
                <IconButton size="4" variant="classic" radius="full" onClick={handlePlaybackSpeedClick}>
                    {state.playbackRate === 1 ? (
                        <TimerIcon width="24" height="24" />
                    ) : (
                        <LightningBoltIcon width="24" height="24" />
                    )}
                </IconButton>
            </Flex>
            <Flex align={{ initial: "start", sm: "center" }} direction="column">
                <Heading size={{ initial: "5", sm: "6" }} mb="2">
                    {story.title}
                </Heading>
                <Text>{story.description}</Text>
            </Flex>
            <Flex direction={{ initial: "column", sm: "row" }} gap="4">
                {state.currentBranch?.leaf ? (
                    <Button
                        size="4"
                        onClick={handleReload}
                        style={{ width: "150px", height: "150px" }}
                        variant="outline"
                        color="blue"
                    >
                        <ReloadIcon width="100" height="100" />
                    </Button>
                ) : (
                    <>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("positive")}
                            style={{ width: "150px", height: "150px" }}
                            variant={state.sentiment === "positive" ? "solid" : "outline"}
                            color="green"
                            disabled={!state.currentBranch}
                        >
                            <PlusIcon width="100" height="100" />
                        </Button>
                        <Button
                            size="4"
                            onClick={() => handleSentimentChange("negative")}
                            style={{ width: "150px", height: "150px" }}
                            variant={state.sentiment === "negative" ? "solid" : "outline"}
                            color="red"
                            disabled={!state.currentBranch}
                        >
                            <MinusIcon width="100" height="100" />
                        </Button>
                    </>
                )}
            </Flex>
            {/* biome-ignore lint/a11y/useMediaCaption: Not for now. */}
            <audio ref={audioRef} style={{ display: "none" }} />
        </Flex>
    )
}

function preloadUpcomingBranches(currentBranch: Branch | null, sentiment?: "positive" | "negative") {
    if (!currentBranch) {
        console.warn("Cannot preload upcoming branches: currentBranch is null")
        return
    }
    if (!sentiment || sentiment === "positive") {
        if (currentBranch.positive_branch_id) {
            getBranch(currentBranch.story_id, currentBranch.positive_branch_id)
        } else {
            console.warn("Cannot preload positive branch: positive_branch_id is null")
        }
    }
    if (!sentiment || sentiment === "negative") {
        if (currentBranch.negative_branch_id) {
            getBranch(currentBranch.story_id, currentBranch.negative_branch_id)
        } else {
            console.warn("Cannot preload negative branch: negative_branch_id is null")
        }
    }
}

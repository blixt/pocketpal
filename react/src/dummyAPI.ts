import type { Branch, Story } from "./api"
import demoAudio from "./demo/demo.mp3?url"
export type { Branch, Story } from "./api"

const dummyStory: Story = {
    id: "dummy-story-id",
    initial_branch_id: "dummy-initial-branch-id",
    title: "Dummy Story Title",
    description: "This is a dummy story description.",
    initial_prompt: "Once upon a time...",
}

const dummyBranch: Branch = {
    id: "dummy-branch-id",
    story_id: "dummy-story-id",
    previous_id: null,
    status: "done",
    audio_url: demoAudio,
    story: "This is a dummy story branch content.",
    positive_branch_id: "dummy-positive-branch-id",
    negative_branch_id: "dummy-negative-branch-id",
}

export async function createStory(initialPrompt: string): Promise<Story> {
    console.log("Creating dummy story with prompt:", initialPrompt)
    return Promise.resolve({ ...dummyStory, initial_prompt: initialPrompt })
}

export async function getStory(storyId: string): Promise<Story> {
    console.log("Getting dummy story with ID:", storyId)
    return Promise.resolve({ ...dummyStory, id: storyId })
}

export async function getBranch(storyId: string, branchId: string): Promise<Branch> {
    console.log("Getting dummy branch with story ID:", storyId, "and branch ID:", branchId)
    return Promise.resolve({ ...dummyBranch, story_id: storyId, id: branchId })
}

export async function generateBranch(
    storyId: string,
    branchId: string,
    sentiment: "positive" | "negative",
): Promise<Branch> {
    console.log("Generating dummy branch with story ID:", storyId, "branch ID:", branchId, "and sentiment:", sentiment)
    return Promise.resolve({
        ...dummyBranch,
        story_id: storyId,
        previous_id: branchId,
        id: `dummy-${sentiment}-branch-id`,
    })
}

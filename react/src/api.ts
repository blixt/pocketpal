const API_BASE_URL = "/v1"

export interface Story {
    id: string
    initial_branch_id: string
    title: string
    description: string
    initial_prompt: string
    lang: string
}

export interface Branch {
    id: string
    story_id: string
    previous_branch_id: string | null
    status: "new" | "generating-text" | "text-only" | "generating-audio" | "done" | "failed"
    sentiment: "initial_branch" | "positive" | "negative"
    audio_url: string | null
    paragraph: string | null
    positive_branch_id: string
    negative_branch_id: string
    final_branch: boolean
}

const pendingBranchRequests: Record<string, Promise<Branch>> = {}

async function api<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
        const url = `${API_BASE_URL}${endpoint}`
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
        })
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        return await response.json()
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error)
        throw error
    }
}

export async function createStory(initialPrompt: string): Promise<{ story: Story; initial_branch: Branch }> {
    return api("/stories/", {
        method: "POST",
        body: JSON.stringify({ initial_prompt: initialPrompt }),
    })
}

export async function getStory(storyId: string): Promise<Story> {
    return api(`/stories/${storyId}/`)
}

export async function getBranch(storyId: string, branchId: string): Promise<Branch> {
    const key = `${storyId}:${branchId}`
    if (!pendingBranchRequests[key]) {
        pendingBranchRequests[key] = api(`/stories/${storyId}/branches/${branchId}/`)
        pendingBranchRequests[key].finally(() => {
            delete pendingBranchRequests[key]
        })
    }
    return pendingBranchRequests[key]
}

export async function generateBranch(
    storyId: string,
    branchId: string,
    sentiment: "positive" | "negative",
): Promise<Branch> {
    const key = `${storyId}:${branchId}:${sentiment}`
    if (!pendingBranchRequests[key]) {
        pendingBranchRequests[key] = api(`/stories/${storyId}/branches/${branchId}/generate`, {
            method: "POST",
            body: JSON.stringify({ sentiment }),
        })
        pendingBranchRequests[key].finally(() => {
            delete pendingBranchRequests[key]
        })
    }
    return pendingBranchRequests[key]
}

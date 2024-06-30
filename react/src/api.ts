const API_BASE_URL = "/v1"

export interface Story {
    id: string
    initial_branch_id: string
    title: string
    description: string
    initial_prompt: string
}

export interface Branch {
    id: string
    story_id: string
    previous_id: string | null
    status: "new" | "generating" | "done" | "failed"
    audio_url: string
    story: string
    positive_branch_id: string | null
    negative_branch_id: string | null
    leaf: boolean
}

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

export async function createStory(initialPrompt: string): Promise<Story> {
    return api("/story/", {
        method: "POST",
        body: JSON.stringify({ initial_prompt: initialPrompt }),
    })
}

export async function getStory(storyId: string): Promise<Story> {
    return api(`/story/${storyId}/`)
}

export async function getBranch(storyId: string, branchId: string): Promise<Branch> {
    return api(`/story/${storyId}/branches/${branchId}/`)
}

export async function generateBranch(
    storyId: string,
    branchId: string,
    sentiment: "positive" | "negative",
): Promise<Branch> {
    return api(`/story/${storyId}/branches/${branchId}/generate`, {
        method: "POST",
        body: JSON.stringify({ sentiment }),
    })
}

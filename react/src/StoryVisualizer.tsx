import { Flex } from "@radix-ui/themes"
import * as d3 from "d3"
import { useEffect, useRef, useState } from "react"
import { getBranch, type Story } from "./api"

interface Node extends d3.SimulationNodeDatum {
    id: string
    audioUrl: string
    sentiment: "positive" | "negative" | "initial"
}

interface Link extends d3.SimulationLinkDatum<Node> {
    source: string | Node
    target: string | Node
    sentiment: "positive" | "negative"
}

interface StoryVisualizerProps {
    story: Story
}

function StoryVisualizer({ story }: StoryVisualizerProps) {
    const svgRef = useRef<SVGSVGElement>(null)
    const audioRef = useRef<HTMLAudioElement>(null)
    const [nodes, setNodes] = useState<Node[]>([])
    const [links, setLinks] = useState<Link[]>([])
    const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)

    useEffect(() => {
        const fetchBranches = async (
            branchId: string,
            parentId: string | null = null,
            sentiment: "positive" | "negative" | "initial" = "initial",
        ) => {
            const branch = await getBranch(story.id, branchId)
            const newNode: Node = { id: branch.id, audioUrl: branch.audio_url, sentiment }
            setNodes(prevNodes => [...prevNodes, newNode])

            if (parentId && sentiment !== "initial") {
                const newLink: Link = {
                    source: parentId,
                    target: branch.id,
                    sentiment: sentiment,
                }
                setLinks(prevLinks => [...prevLinks, newLink])
            }

            if (branch.positive_branch_id) {
                await fetchBranches(branch.positive_branch_id, branch.id, "positive")
            }
            if (branch.negative_branch_id) {
                await fetchBranches(branch.negative_branch_id, branch.id, "negative")
            }
        }

        fetchBranches(story.initial_branch_id)
    }, [story])

    useEffect(() => {
        if (!svgRef.current || nodes.length === 0) return

        const width = 800
        const height = 600

        const svg = d3.select(svgRef.current).attr("width", width).attr("height", height)

        // Clear previous content
        svg.selectAll("*").remove()

        const simulation = d3
            .forceSimulation(nodes)
            .force(
                "link",
                d3
                    .forceLink<Node, Link>(links)
                    .id(d => d.id)
                    .distance(100),
            )
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))

        // Create a group for links
        const linkGroup = svg.append("g")

        const link = linkGroup
            .selectAll(".link")
            .data(links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", d => (d.sentiment === "positive" ? "rgba(0, 255, 0, 0.6)" : "rgba(255, 0, 0, 0.6)")) // Green for positive, Red for negative
            .attr("stroke-width", 2)

        // Create a group for nodes
        const nodeGroup = svg.append("g")

        const node = nodeGroup
            .selectAll<SVGGElement, Node>(".node")
            .data(nodes)
            .join("g")
            .attr("class", "node")
            .call(drag(simulation))

        node.append("circle")
            .attr("r", 20)
            .attr("fill", d => {
                if (d.sentiment === "positive") return "rgb(0, 255, 0)" // Green
                if (d.sentiment === "negative") return "rgb(255, 0, 0)" // Red
                return "rgb(173, 216, 230)" // Light blue for initial
            })

        const textElement = node
            .append("text")
            .attr("text-anchor", "middle")
            .attr("dy", ".35em")
            .text(d => (d.id === currentlyPlaying ? "⏹" : "▶"))
            .attr("fill", "white")

        node.append("title").text(d => d.id)

        simulation.on("tick", () => {
            link.attr("x1", d => (d.source as Node).x ?? 0)
                .attr("y1", d => (d.source as Node).y ?? 0)
                .attr("x2", d => (d.target as Node).x ?? 0)
                .attr("y2", d => (d.target as Node).y ?? 0)

            node.attr("transform", d => `translate(${d.x ?? 0},${d.y ?? 0})`)
        })

        node.on("click", (_, d: Node) => {
            if (currentlyPlaying === d.id) {
                audioRef.current?.pause()
                setCurrentlyPlaying(null)
            } else {
                audioRef.current?.pause()
                if (audioRef.current) {
                    audioRef.current.src = d.audioUrl
                    audioRef.current.play()
                }
                setCurrentlyPlaying(d.id)
            }
            // Update all text elements
            textElement.text(node => (node.id === d.id ? (currentlyPlaying === d.id ? "▶" : "⏹") : "▶"))
        })

        return () => {
            simulation.stop()
        }
    }, [nodes, links, currentlyPlaying])

    const drag = (simulation: d3.Simulation<Node, undefined>) => {
        function dragstarted(event: d3.D3DragEvent<SVGGElement, Node, Node>) {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            event.subject.fx = event.subject.x
            event.subject.fy = event.subject.y
        }

        function dragged(event: d3.D3DragEvent<SVGGElement, Node, Node>) {
            event.subject.fx = event.x
            event.subject.fy = event.y
        }

        function dragended(event: d3.D3DragEvent<SVGGElement, Node, Node>) {
            if (!event.active) simulation.alphaTarget(0)
            event.subject.fx = null
            event.subject.fy = null
        }

        return d3.drag<SVGGElement, Node>().on("start", dragstarted).on("drag", dragged).on("end", dragended)
    }

    return (
        <Flex direction="column" align="center">
            <svg ref={svgRef} />
            {/* biome-ignore lint/a11y/useMediaCaption: Not for now. */}
            <audio ref={audioRef} style={{ display: "none" }} />
        </Flex>
    )
}

export default StoryVisualizer

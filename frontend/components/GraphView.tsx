"use client"

import { useEffect, useRef } from "react"
import { buildGraph } from "../lib/graphTransform"
import { ForensicResponse } from "../types/forensic"

export default function GraphView({
  data,
  suspiciousOnly,
  highlightedAccount,
  selectedRing,
  onNodeClick
}: {
  data: ForensicResponse
  suspiciousOnly: boolean
  highlightedAccount: string | null
  selectedRing: string | null
  onNodeClick: (id: string) => void
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const rendererRef = useRef<any>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    let mounted = true

    import("sigma").then(async (SigmaModule) => {
      if (!mounted) return

      const Sigma = SigmaModule.default

      // 🔥 Kill previous renderer
      if (rendererRef.current) {
        rendererRef.current.kill()
        rendererRef.current = null
      }

      const graph = buildGraph(
        data,
        suspiciousOnly,
        highlightedAccount,
        selectedRing
      )

      const renderer = new Sigma(graph, containerRef.current!)
      rendererRef.current = renderer

      // 🔷 Click interaction
      renderer.on("clickNode", ({ node }) => {
        const camera = renderer.getCamera()

        const nodeData = graph.getNodeAttributes(node)

        // Keep current zoom
        const currentRatio = camera.getState().ratio

        camera.animate(
          {
            x: nodeData.x,
            y: nodeData.y,
            ratio: currentRatio, // preserve zoom
          },
          {
            duration: 600
          }
        )

        onNodeClick(node)
      })

      // 🔷 Hover enter
      renderer.on("enterNode", (event: any) => {
        const nodeId = event.node

        const account = data.suspicious_accounts.find(
          (a) => a.account_id === nodeId
        )

        if (!tooltipRef.current) return

        const tooltip = tooltipRef.current
        tooltip.style.display = "block"

        tooltip.innerHTML = `
          <strong>${nodeId}</strong><br/>
          Suspicion: ${account?.suspicion_score ?? 0}<br/>
          Patterns: ${
            account?.detected_patterns.join(", ") ?? "None"
          }
        `
      })

      renderer.on("leaveNode", () => {
        if (tooltipRef.current) {
          tooltipRef.current.style.display = "none"
        }
      })

      // renderer.on("mousemove", (event) => {
      //   if (!tooltipRef.current) return

      //   const tooltip = tooltipRef.current
      //   const rect = containerRef.current!.getBoundingClientRect()

      //   tooltip.style.left = `${event.event.clientX - rect.left + 15}px`
      //   tooltip.style.top = `${event.event.clientY - rect.top + 15}px`
      // })

      // 🔷 Version-safe animated force layout
      const forceLayoutModule: any = await import(
        "graphology-layout-force"
      )
      const forceLayout = forceLayoutModule.default

      let iterations = 0
      const maxIterations = 200

      const interval = setInterval(() => {
        forceLayout.assign(graph, {
          maxIterations: 1
        })

        renderer.refresh()

        iterations++
        if (iterations >= maxIterations) {
          clearInterval(interval)
        }
      }, 16) // ~60fps

      // 🔷 Camera logic
      const camera = renderer.getCamera()

      if (
        highlightedAccount &&
        graph.hasNode(highlightedAccount)
      ) {
        const { x, y } = graph.getNodeAttributes(
          highlightedAccount
        )

        camera.animate(
          {
            x,
            y,
            ratio: 0.5
          },
          {
            duration: 600
          }
        )
      } else {
        camera.animatedReset()
      }
    })

    return () => {
      mounted = false

      if (rendererRef.current) {
        rendererRef.current.kill()
        rendererRef.current = null
      }
    }
  }, [data, suspiciousOnly, highlightedAccount, selectedRing])

  return (
    <div style={{ position: "relative" }}>
      <div
        ref={containerRef}
        style={{
          height: "600px",
          width: "100%",
          background: "white",
          border: "1px solid #ddd"
        }}
      />

      {/* 🔷 Tooltip */}
      <div
        ref={tooltipRef}
        style={{
          position: "absolute",
          display: "none",
          background: "white",
          border: "1px solid #ddd",
          padding: "8px 12px",
          borderRadius: "6px",
          fontSize: "12px",
          pointerEvents: "none",
          boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          zIndex: 10
        }}
      />
    </div>
  )
}



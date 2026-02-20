import Graph from "graphology"
import { ForensicResponse } from "../types/forensic"

export function buildGraph(
  data: ForensicResponse,
  suspiciousOnly: boolean,
  highlightedAccount: string | null,
  selectedRing: string | null
) {
  const graph = new Graph()

  const suspiciousMap = new Map(
    data.suspicious_accounts.map(a => [a.account_id, a])
  )

  const accounts = new Set<string>()

  // 🔷 Collect accounts based on selected ring + suspicious filter
  data.fraud_rings.forEach(ring => {
    if (selectedRing && ring.ring_id !== selectedRing) return

    ring.member_accounts.forEach(account => {
      if (!suspiciousOnly || suspiciousMap.has(account)) {
        accounts.add(account)
      }
    })
  })

  const accountList = Array.from(accounts)

  if (accountList.length === 0) return graph

  const radius = 10

  // 🔷 Add nodes
  accountList.forEach((account, i) => {
    const angle = (i / accountList.length) * 2 * Math.PI

    const suspicion = suspiciousMap.get(account)?.suspicion_score || 0
    const isHighlighted = highlightedAccount === account

    graph.addNode(account, {
      label: account,
      size: isHighlighted ? 16 : 6 + suspicion / 10,
      color: isHighlighted
        ? "#0066ff"
        : getColor(suspicion),
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius
    })
  })

  // 🔷 Add edges
  data.fraud_rings.forEach(ring => {
    if (selectedRing && ring.ring_id !== selectedRing) return

    const members = ring.member_accounts

    for (let i = 0; i < members.length; i++) {
      const a = members[i]
      const b = members[(i + 1) % members.length]

      if (graph.hasNode(a) && graph.hasNode(b)) {
        const edgeId = `${a}-${b}-${ring.ring_id}`

        if (!graph.hasEdge(edgeId)) {
          graph.addEdgeWithKey(edgeId, a, b, {
            color:
              highlightedAccount &&
              (a === highlightedAccount || b === highlightedAccount)
                ? "#0066ff"
                : "#ccc"
          })
        }
      }
    }
  })

  return graph
}

// 🔷 Suspicion Heat Scale
function getColor(score: number) {
  if (score > 80) return "#ff0000"
  if (score > 60) return "#ff6600"
  if (score > 40) return "#ffaa00"
  return "#ffd700"
}

"use client"

import { useState } from "react"
import UploadPanel from "../components/UploadPanel"
import GraphView from "../components/GraphView"
import RingTable from "../components/RingTable"
import RiskAnalytics from "../components/RiskAnalytics"
import { exportReport } from "../lib/exportReport"
import { ForensicResponse } from "../types/forensic"
import CSVSummaryPanel from "../components/CSVSummaryPanel"
import NodeIntelligencePanel from "../components/NodeIntelligencePanel"


export default function Home() {
  const [data, setData] = useState<ForensicResponse | null>(null)
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)
  const [selectedRing, setSelectedRing] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [suspiciousOnly, setSuspiciousOnly] = useState(false)
  

  return (
    <main>
      <div className="container">

        {/* ===== FIXED HEADER ===== */}
        <div className="header-section">
          <h1 className="brand">GolMaal</h1>

          <div className="upload-wrapper">
            <UploadPanel onData={setData} />
          </div>
        </div>

        {/* ===== BELOW THIS CONTENT CAN CHANGE ===== */}

        {data && (
          <>
            <div className="workspace">

              {/* LEFT: SUMMARY */}
              <div className="left-panel">

                <CSVSummaryPanel data={data} />

                <div className="search-panel">
                  <input
                    className="search-input"
                    placeholder="Search account..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />

                  <button
                    className="search-button"
                    onClick={() =>
                      setSelectedAccount(searchQuery.trim().toUpperCase())
                    }
                  >
                    Search
                  </button>
                </div>

              </div>


              {/* RIGHT: GRAPH */}
              <div className="right-panel">
                <div className="graph-arena">
                  <GraphView
                    data={data}
                    suspiciousOnly={suspiciousOnly}
                    highlightedAccount={selectedAccount}
                    selectedRing={selectedRing}
                    onNodeClick={(id) => setSelectedAccount(id)}
                  />
                </div>
              </div>

            </div>

            <NodeIntelligencePanel
              selectedAccount={selectedAccount}
              data={data}
            />

            <RiskAnalytics data={data} />

            <button
              className="download-btn"
              onClick={() => exportReport(data)}
            >
              Download Full JSON Report
            </button>

            <div className="table-section">
              <RingTable
                rings={data.fraud_rings}
                selectedRing={selectedRing}
                onSelectRing={setSelectedRing}
              />
            </div>
          </>
        )}

      </div>
    </main>
  )
}

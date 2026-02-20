"use client"

import { ForensicResponse } from "../types/forensic"

export default function NodeIntelligencePanel({
  selectedAccount,
  data
}: {
  selectedAccount: string | null
  data: ForensicResponse
}) {
  if (!selectedAccount) return null

  const account = data.suspicious_accounts.find(
    (a) => a.account_id === selectedAccount
  )

  if (!account) {
    return (
      <div className="node-panel">
        <h2 className="node-title">Node Intelligence</h2>
        <div className="node-content">
          <div className="node-label">Account ID</div>
          <div className="node-value">{selectedAccount}</div>
          <div className="node-note">
            No suspicious patterns detected.
          </div>
        </div>
      </div>
    )
  }

  const riskLevel =
    account.suspicion_score > 70
      ? "High"
      : account.suspicion_score > 40
      ? "Medium"
      : "Low"

  return (
    <div className="node-panel">
      <h2 className="node-title">Node Intelligence</h2>

      <div className="node-grid">
        <div>
          <div className="node-label">Account ID</div>
          <div className="node-value">{account.account_id}</div>
        </div>

        <div>
          <div className="node-label">Suspicion Score</div>
          <div className="node-value">
            {account.suspicion_score.toFixed(1)}
          </div>
        </div>

        <div>
          <div className="node-label">Risk Level</div>
          <div className={`risk-badge risk-${riskLevel.toLowerCase()}`}>
            {riskLevel}
          </div>
        </div>

        <div>
          <div className="node-label">Ring ID</div>
          <div className="node-value">{account.ring_id}</div>
        </div>
      </div>

      <div className="patterns-section">
        <div className="node-label">Detected Patterns</div>
        <div className="patterns-list">
          {account.detected_patterns.map((p, idx) => (
            <span key={idx} className="pattern-pill">
              {p}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
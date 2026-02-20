"use client"

import { ForensicResponse } from "../types/forensic"

export default function CSVSummaryPanel({
  data
}: {
  data: ForensicResponse
}) {
  return (
    <div className="summary-panel">
      <h2 className="summary-title">CSV Intelligence Summary</h2>

      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-label">Total Accounts</div>
          <div className="summary-value">
            {data.summary.total_accounts_analyzed}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Suspicious Accounts</div>
          <div className="summary-value">
            {data.summary.suspicious_accounts_flagged}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Fraud Rings</div>
          <div className="summary-value">
            {data.summary.fraud_rings_detected}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Processing Time</div>
          <div className="summary-value">
            {data.summary.processing_time_seconds}s
          </div>
        </div>
      </div>
    </div>
  )
}

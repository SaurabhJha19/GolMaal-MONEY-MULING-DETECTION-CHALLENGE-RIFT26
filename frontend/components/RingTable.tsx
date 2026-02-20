"use client"

type Ring = {
  ring_id: string
  member_accounts: string[]
  pattern_type: string
  risk_score: number
}

export default function RingTable({
  rings,
  selectedRing,
  onSelectRing
}: {
  rings: Ring[]
  selectedRing: string | null
  onSelectRing: (id: string) => void
}) {
  if (!rings || rings.length === 0) return null

  return (
    <div className="ring-table-wrapper">
      <h2 className="ring-table-title">Fraud Ring Summary</h2>

      <div className="ring-table-container">
        <table className="ring-table">
          <thead>
            <tr>
              <th>Ring ID</th>
              <th>Pattern Type</th>
              <th>Members</th>
              <th>Risk Score</th>
              <th>Accounts</th>
            </tr>
          </thead>

          <tbody>
            {rings.map((ring) => (
              <tr
                key={ring.ring_id}
                className={
                  selectedRing === ring.ring_id ? "active-row" : ""
                }
                onClick={() => onSelectRing(ring.ring_id)}
              >
                <td>{ring.ring_id}</td>
                <td className="pattern-cell">
                  {ring.pattern_type}
                </td>
                <td>{ring.member_accounts.length}</td>
                <td className="risk-cell">
                  {ring.risk_score.toFixed(1)}
                </td>
                <td className="accounts-cell">
                  {ring.member_accounts.join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
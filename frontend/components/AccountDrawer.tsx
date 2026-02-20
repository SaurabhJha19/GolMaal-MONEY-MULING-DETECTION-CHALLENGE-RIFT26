"use client"

import { SuspiciousAccount, ForensicResponse } from "../types/forensic"

interface Props {
  selectedAccount: string | null
  data: ForensicResponse
  onClose: () => void
}

export default function AccountDrawer({
  selectedAccount,
  data,
  onClose
}: Props) {
  if (!selectedAccount) return null

  const account = data.suspicious_accounts.find(
    (a) => a.account_id === selectedAccount
  )

  return (
    <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl p-6 z-50 transition-transform">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">
          Account Intelligence
        </h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-black"
        >
          ✕
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-sm text-gray-500">Account ID</h3>
          <p className="text-lg font-medium">{selectedAccount}</p>
        </div>

        {account ? (
          <>
            <div>
              <h3 className="text-sm text-gray-500">Suspicion Score</h3>
              <p className="text-2xl font-bold text-red-600">
                {account.suspicion_score}
              </p>
            </div>

            <div>
              <h3 className="text-sm text-gray-500">Detected Patterns</h3>
              <ul className="list-disc list-inside">
                {account.detected_patterns.map((pattern, i) => (
                  <li key={i}>{pattern}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm text-gray-500">Ring ID</h3>
              <p className="font-mono text-sm">
                {account.ring_id}
              </p>
            </div>
          </>
        ) : (
          <p className="text-gray-500">
            No suspicious patterns detected.
          </p>
        )}
      </div>
    </div>
  )
}

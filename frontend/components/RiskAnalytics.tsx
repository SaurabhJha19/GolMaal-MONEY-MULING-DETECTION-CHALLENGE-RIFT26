"use client"

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js"
import { Bar } from "react-chartjs-2"
import { ForensicResponse } from "../types/forensic"

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export default function RiskAnalytics({
  data
}: {
  data: ForensicResponse
}) {
  const suspicious = data.suspicious_accounts

  const low = suspicious.filter(a => a.suspicion_score <= 40).length
  const medium = suspicious.filter(
    a => a.suspicion_score > 40 && a.suspicion_score <= 60
  ).length
  const high = suspicious.filter(a => a.suspicion_score > 60).length

  const patternCounts: Record<string, number> = {}

  suspicious.forEach(acc => {
    acc.detected_patterns.forEach(p => {
      patternCounts[p] = (patternCounts[p] || 0) + 1
    })
  })

  const baseOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#ffffff",
          font: {
            size: 14,
            weight: "600"
          }
        }
      },
      tooltip: {
        backgroundColor: "#0f172a",
        titleColor: "#ffffff",
        bodyColor: "#e2e8f0",
        borderColor: "#334155",
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: {
          color: "#cbd5e1",
          font: { size: 13 }
        },
        grid: {
          color: "rgba(255,255,255,0.05)"
        }
      },
      y: {
        ticks: {
          color: "#cbd5e1",
          font: { size: 13 }
        },
        grid: {
          color: "rgba(255,255,255,0.05)"
        }
      }
    }
  }

  const distributionData = {
    labels: ["Low (0–40)", "Medium (40–60)", "High (60+)"],
    datasets: [
      {
        label: "Accounts",
        data: [low, medium, high],
        backgroundColor: [
          "#38bdf8",  // cyan
          "#facc15",  // amber
          "#ef4444"   // red
        ],
        borderRadius: 10,
        barThickness: 60
      }
    ]
  }

  const patternData = {
    labels: Object.keys(patternCounts),
    datasets: [
      {
        label: "Pattern Frequency",
        data: Object.values(patternCounts),
        backgroundColor: "#3b82f6",
        borderRadius: 10,
        barThickness: 60
      }
    ]
  }

  return (
    <div className="analytics-wrapper">
      <div className="chart-card">
        <Bar data={distributionData} options={baseOptions} />
      </div>

      <div className="chart-card">
        <Bar data={patternData} options={baseOptions} />
      </div>
    </div>
  )
}

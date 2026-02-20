import { ForensicResponse } from "../types/forensic"

export function exportReport(data: ForensicResponse) {
  const timestamp = new Date()
    .toISOString()
    .replace(/[:.]/g, "-")

  const filename = `forensic-report-${timestamp}.json`

  const jsonString = JSON.stringify(data, null, 2)

  const blob = new Blob([jsonString], {
    type: "application/json"
  })

  const url = URL.createObjectURL(blob)

  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()

  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

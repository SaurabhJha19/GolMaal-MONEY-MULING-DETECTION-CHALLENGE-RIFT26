"use client"

import { useRef } from "react"
import { analyzeFile } from "../lib/api"

export default function UploadPanel({
  onData
}: {
  onData: any
}) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    const result = await analyzeFile(file)
    onData(result)
  }

  return (
    <div className="upload-outer">
      <div
        className="upload-inner"
        onClick={() => fileInputRef.current?.click()}
      >
        Upload your CSV File
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleUpload}
        style={{ display: "none" }}
      />
    </div>
  )
}

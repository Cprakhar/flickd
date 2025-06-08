import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const res = await fetch(`${backendUrl}/api/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (error) {
    console.error("Error in /api/recommendations:", error)
    return NextResponse.json({ status: "error", message: "Internal server error" }, { status: 500 })
  }
}
import { NextResponse } from "next/server"
import type { RecommendationApiResponse, RecommendationData, ProductRecommendation } from "@/lib/types"

const sampleProducts: Omit<ProductRecommendation, "matched_product_id" | "confidence" | "match_type">[] = [
  {
    type: "top",
    name: "Classic White Tee",
    color: "white",
    image_url: "/placeholder.svg?width=100&height=120&text=White+Tee",
    price: "$25",
  },
  {
    type: "bottom",
    name: "Distressed Denim Jeans",
    color: "blue",
    image_url: "/placeholder.svg?width=100&height=120&text=Blue+Jeans",
    price: "$60",
  },
  {
    type: "shoes",
    name: "Minimalist Sneakers",
    color: "white",
    image_url: "/placeholder.svg?width=100&height=120&text=Sneakers",
    price: "$80",
  },
  {
    type: "accessory",
    name: "Gold Hoop Earrings",
    color: "gold",
    image_url: "/placeholder.svg?width=100&height=120&text=Earrings",
    price: "$35",
  },
  {
    type: "outerwear",
    name: "Beige Trench Coat",
    color: "beige",
    image_url: "/placeholder.svg?width=100&height=120&text=Trench+Coat",
    price: "$120",
  },
  {
    type: "dress",
    name: "Floral Sundress",
    color: "multi",
    image_url: "/placeholder.svg?width=100&height=120&text=Sundress",
    price: "$70",
  },
]

const sampleVibes = ["Casual Cool", "Street Style", "Minimalist", "Chic", "Boho", "Edgy", "Preppy", "Vintage"]

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { videoUrl, caption, hashtags } = body

    if (!videoUrl) {
      return NextResponse.json({ status: "error", message: "videoUrl is required" }, { status: 400 })
    }

    // Simulate ML processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Generate mock recommendations
    const numProducts = Math.floor(Math.random() * 3) + 1 // 1 to 3 products
    const products: ProductRecommendation[] = []
    const usedProductIndices = new Set<number>()

    for (let i = 0; i < numProducts; i++) {
      let productIndex
      do {
        productIndex = Math.floor(Math.random() * sampleProducts.length)
      } while (usedProductIndices.has(productIndex))
      usedProductIndices.add(productIndex)

      products.push({
        ...sampleProducts[productIndex],
        matched_product_id: `prod_${String(Math.random()).slice(2, 8)}`,
        confidence: Math.random() * 0.3 + 0.7, // 0.7 to 1.0
        match_type: Math.random() > 0.5 ? "exact" : "similar",
      })
    }

    const numVibes = Math.floor(Math.random() * 2) + 1 // 1 to 2 vibes
    const vibes: string[] = []
    const usedVibeIndices = new Set<number>()
    for (let i = 0; i < numVibes; i++) {
      let vibeIndex
      do {
        vibeIndex = Math.floor(Math.random() * sampleVibes.length)
      } while (usedVibeIndices.has(vibeIndex))
      usedVibeIndices.add(vibeIndex)
      vibes.push(sampleVibes[vibeIndex])
    }

    const videoIdFromUrl = videoUrl.split("/").pop()?.split(".")[0] || "unknown_video"

    const recommendationData: RecommendationData = {
      video_id: body.video_id || videoIdFromUrl,
      vibes,
      products,
    }

    const response: RecommendationApiResponse = {
      status: "success",
      data: recommendationData,
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error("Error in /api/recommendations:", error)
    return NextResponse.json({ status: "error", message: "Internal server error" }, { status: 500 })
  }
}

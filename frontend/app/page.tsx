"use client"

import { useRef } from "react"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import { VideoFeed } from "@/components/video-feed"
import { RecommendationSidebar } from "@/components/recommendation-sidebar"
import type { Video, RecommendationData, VideosApiResponse, RecommendationApiResponse } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ArrowUp } from "lucide-react"

const backendUrl = process.env.NEXT_PUBLIC_API_URL // Adjust if your API is hosted elsewhere

export default function HomePage() {
  const [initialVideos, setInitialVideos] = useState<Video[]>([])
  const [isLoadingInitial, setIsLoadingInitial] = useState(true)
  const [nextPage, setNextPage] = useState<number | null>(1)

  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [currentRecommendations, setCurrentRecommendations] = useState<RecommendationData | null>(null)
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false)

  const [showScrollTop, setShowScrollTop] = useState(false)
  const feedContainerRef = useRef<HTMLDivElement>(null)

  const fetchVideos = useCallback(async (pageToFetch: number): Promise<Video[] | null> => {
    if (pageToFetch === null) return null
    try {
      const response = await fetch(`/api/videos?page=${pageToFetch}`)
      if (!response.ok) {
        console.error("Failed to fetch videos:", response.statusText)
        setNextPage(null) // Stop trying if error
        return null
      }
      const result: VideosApiResponse = await response.json()
      if (result.status === "success") {
        setNextPage(result.next_page !== undefined ? result.next_page : null)
        return result.data
      } else {
        console.error("Error fetching videos:", result.message)
        setNextPage(null)
        return null
      }
    } catch (error) {
      console.error("Error fetching videos:", error)
      setNextPage(null)
      return null
    }
  }, [])

  useEffect(() => {
    const loadInitialVideos = async () => {
      setIsLoadingInitial(true)
      const videos = await fetchVideos(1)
      if (videos) {
        setInitialVideos(videos)
      }
      setIsLoadingInitial(false)
    }
    loadInitialVideos()
  }, [fetchVideos])

  const handleLoadMore = async (): Promise<Video[] | null> => {
    if (nextPage === null) return null
    return fetchVideos(nextPage)
  }

  const handleRecommend = async (video: Video) => {
    setIsRecommendationLoading(true)
    setCurrentRecommendations(null) // Clear previous recommendations
    setIsSidebarOpen(true)
    try {
      const response = await fetch(`${backendUrl}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          videoUrl: video.video_url,
          caption: video.caption,
          hashtags: video.hashtags,
          video_id: video.video_id, // Pass video_id for better mock response
        }),
      })
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }
      const result = await response.json()
      if (result.status === "success") {
        setCurrentRecommendations(result.data)
        setIsRecommendationLoading(false)
        return
      }
      // If status is pending, poll the status endpoint
      if (result.status === "pending" && result.video_id) {
        const pollStatus = async () => {
          let attempts = 0
          const maxAttempts = 60 * 5 // e.g. 60 x 1s = 1 minute
          while (attempts < maxAttempts) {
            await new Promise((res) => setTimeout(res, 1000))
            const statusRes = await fetch(`${backendUrl}/api/recommendations/status/${result.video_id}`)
            if (!statusRes.ok) {
              attempts++
              continue
            }
            const statusJson = await statusRes.json()
            if (statusJson.status === "success") {
              setCurrentRecommendations(statusJson.data)
              setIsRecommendationLoading(false)
              return
            } else if (statusJson.status === "error") {
              setCurrentRecommendations({ video_id: video.video_id, vibes: ["Error"], products: [] })
              setIsRecommendationLoading(false)
              return
            }
            // else: still running, keep polling
            attempts++
          }
          // Timed out
          setCurrentRecommendations({ video_id: video.video_id, vibes: ["Timeout"], products: [] })
          setIsRecommendationLoading(false)
        }
        pollStatus()
        return
      }
      // Unknown state
      setCurrentRecommendations({ video_id: video.video_id, vibes: ["Unknown Error"], products: [] })
    } catch (error) {
      console.error("Error fetching recommendations:", error)
      setCurrentRecommendations({ video_id: video.video_id, vibes: ["Network Error"], products: [] })
      setIsRecommendationLoading(false)
    }
  }

  // Scroll to top logic
  const videoFeedElement = typeof document !== "undefined" ? document.querySelector(".snap-y.snap-mandatory") : null

  useEffect(() => {
    const handleScroll = () => {
      if (videoFeedElement) {
        setShowScrollTop(videoFeedElement.scrollTop > 300)
      }
    }

    if (videoFeedElement) {
      videoFeedElement.addEventListener("scroll", handleScroll)
      return () => videoFeedElement.removeEventListener("scroll", handleScroll)
    }
  }, [videoFeedElement])

  const scrollToTop = () => {
    if (videoFeedElement) {
      videoFeedElement.scrollTo({ top: 0, behavior: "smooth" })
    }
  }

  if (isLoadingInitial && initialVideos.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <Loader2 className="h-16 w-16 animate-spin text-teal-500" />
      </div>
    )
  }

  return (
    <div ref={feedContainerRef} className="h-screen flex flex-col bg-neutral-900 text-white mx-auto">
      {/* <header className="hidden sm:flex h-16 md:h-20 bg-neutral-900 border-b border-neutral-700 items-center justify-center sticky top-0 z-20">
        <h1 className="text-3xl font-bold" style={{ color: '#8154a4' }}>Flickd</h1>
      </header> */}

      <main className="flex-1 overflow-hidden">
        <VideoFeed initialVideos={initialVideos} onLoadMore={handleLoadMore} onRecommend={handleRecommend} />
      </main>

      <RecommendationSidebar
        isOpen={isSidebarOpen}
        onOpenChange={setIsSidebarOpen}
        recommendations={currentRecommendations}
        isLoading={isRecommendationLoading}
      />

      {showScrollTop && (
        <Button
          onClick={scrollToTop}
          variant="outline"
          size="icon"
          className="fixed bottom-6 right-6 z-50 bg-neutral-800 hover:bg-neutral-700 text-purple-400 border-purple-400 hidden sm:flex"
        >
          <ArrowUp className="h-5 w-5" />
          <span className="sr-only">Scroll to top</span>
        </Button>
      )}
    </div>
  )
}

// Helper component for loading state
const Loader2 = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
)

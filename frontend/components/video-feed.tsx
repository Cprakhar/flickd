"use client"

import { useRef, useCallback, useEffect, useState } from "react"
import type { Video } from "@/lib/types"
import { VideoCard } from "./video-card"
import { Loader2 } from "lucide-react"

interface VideoFeedProps {
  initialVideos: Video[]
  onLoadMore: () => Promise<Video[] | null> // Returns new videos or null if no more
  onRecommend: (video: Video) => void
}

export function VideoFeed({ initialVideos, onLoadMore, onRecommend }: VideoFeedProps) {
  const [videos, setVideos] = useState<Video[]>(initialVideos)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [visibleVideoId, setVisibleVideoId] = useState<string | null>(
    initialVideos.length > 0 ? initialVideos[0].video_id : null,
  )

  const observer = useRef<IntersectionObserver | null>(null)
  const videoCardRefs = useRef<(HTMLDivElement | null)[]>([])
  const loadMoreRef = useRef<HTMLDivElement | null>(null)

  // Observer for individual video cards (visibility for autoplay)
  useEffect(() => {
    const options = {
      root: null,
      rootMargin: "0px",
      threshold: 0.5, // 50% visibility
    }

    const videoObserverCallback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        const videoId = (entry.target as HTMLElement).dataset.videoId
        if (!videoId) return

        if (entry.isIntersecting) {
          setVisibleVideoId(videoId)
        } else {
          // If the video that is no longer intersecting IS the current visibleVideoId,
          // then clear visibleVideoId. This ensures the VideoCard gets isIntersecting={false}.
          if (visibleVideoId === videoId) {
            setVisibleVideoId(null)
          }
        }
      })
    }

    const videoObserver = new IntersectionObserver(videoObserverCallback, options)

    videoCardRefs.current.forEach((ref) => {
      if (ref) videoObserver.observe(ref)
    })

    return () => videoObserver.disconnect()
  }, [videos, visibleVideoId]) // Re-run when videos change to observe new cards

  // Observer for infinite scroll trigger
  const handleLoadMore = useCallback(async () => {
    if (loadingMore || !hasMore) return
    setLoadingMore(true)
    const newVideos = await onLoadMore()
    if (newVideos && newVideos.length > 0) {
      setVideos((prev) => [...prev, ...newVideos])
    } else {
      setHasMore(false)
    }
    setLoadingMore(false)
  }, [onLoadMore, loadingMore, hasMore])

  useEffect(() => {
    const options = {
      root: null,
      rootMargin: "200px", // Load a bit before it's visible
      threshold: 0,
    }

    observer.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore) {
        handleLoadMore()
      }
    }, options)

    if (loadMoreRef.current) {
      observer.current.observe(loadMoreRef.current)
    }

    return () => {
      if (observer.current) {
        observer.current.disconnect()
      }
    }
  }, [handleLoadMore, hasMore])

  // Assign refs to video cards
  useEffect(() => {
    videoCardRefs.current = videoCardRefs.current.slice(0, videos.length)
  }, [videos.length])

  return (
    <div className="h-[calc(100svh-80px)] md:h-[calc(100svh-100px)] w-full overflow-y-auto snap-y snap-mandatory scroll-smooth">
      {videos.map((video, index) => (
        <div
          key={video.video_id}
          ref={(el) => (videoCardRefs.current[index] = el)}
          data-video-id={video.video_id}
          className="snap-center" // Ensures each video card snaps into view
        >
          <VideoCard video={video} onRecommend={onRecommend} isIntersecting={video.video_id === visibleVideoId} />
        </div>
      ))}
      {hasMore && (
        <div ref={loadMoreRef} className="flex justify-center items-center h-20">
          {loadingMore && <Loader2 className="h-8 w-8 animate-spin text-teal-500" />}
        </div>
      )}
      {!hasMore && videos.length > 0 && (
        <div className="flex justify-center items-center h-20 text-sm text-gray-400">You've reached the end!</div>
      )}
      {videos.length === 0 && !loadingMore && (
        <div className="flex justify-center items-center h-full text-gray-400">No videos to show.</div>
      )}
    </div>
  )
}

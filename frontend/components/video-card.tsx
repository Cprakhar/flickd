"use client"

import type React from "react"

import { useRef, useEffect, useState } from "react"
import type { Video } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Sparkles, Play, Volume2, VolumeX, Heart, MessageSquare, Share2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils" // Ensure you have cn utility

interface VideoCardProps {
  video: Video
  onRecommend: (video: Video) => void
  isIntersecting: boolean
}

const MAX_CAPTION_LENGTH_COLLAPSED = 70 // Characters to show when caption is collapsed

export function VideoCard({ video, onRecommend, isIntersecting }: VideoCardProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(true)
  const [isCaptionExpanded, setIsCaptionExpanded] = useState(false)

  const captionIsPotentiallyLong = video.caption && video.caption.length > MAX_CAPTION_LENGTH_COLLAPSED

  useEffect(() => {
    const videoElement = videoRef.current
    if (videoElement) {
      if (isIntersecting) {
        if (videoElement.paused) {
          const playPromise = videoElement.play()
          if (playPromise !== undefined) {
            playPromise
              .then(() => setIsPlaying(true))
              .catch((error) => {
                if (error.name !== "AbortError") {
                  console.error("Error attempting to play video (autoplay):", video.video_id, error)
                }
                setIsPlaying(false)
              })
          }
        } else if (!isPlaying) {
          setIsPlaying(true)
        }
      } else {
        if (!videoElement.paused) {
          videoElement.pause()
        }
        if (isPlaying) setIsPlaying(false)
        // Collapse caption when video is not intersecting
        if (isCaptionExpanded) setIsCaptionExpanded(false)
      }
    }
  }, [isIntersecting, video.video_id, isPlaying, isCaptionExpanded])

  const handleVideoClick = () => {
    // If caption is expanded, clicking video area outside caption should perhaps collapse it?
    // For now, main video click toggles play/pause. Caption click is handled separately.
    togglePlay()
  }

  const togglePlay = () => {
    const videoElement = videoRef.current
    if (videoElement) {
      if (videoElement.paused) {
        const playPromise = videoElement.play()
        if (playPromise !== undefined) {
          playPromise
            .then(() => setIsPlaying(true))
            .catch((error) => {
              if (error.name !== "AbortError") {
                console.error("Error trying to play video (manual toggle):", error)
              }
              setIsPlaying(false)
            })
        }
      } else {
        videoElement.pause()
        setIsPlaying(false)
      }
    }
  }

  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent video click
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted
      setIsMuted(videoRef.current.muted)
    }
  }

  const handleRecommendClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onRecommend(video)
  }

  const toggleCaptionExpansion = (e: React.MouseEvent) => {
    e.stopPropagation() // Important: Prevent video click when interacting with caption
    if (captionIsPotentiallyLong) {
      setIsCaptionExpanded(!isCaptionExpanded)
    }
  }

  const displayedCaption =
    captionIsPotentiallyLong && !isCaptionExpanded
      ? `${video.caption?.substring(0, MAX_CAPTION_LENGTH_COLLAPSED)}... `
      : video.caption

  return (
    <div className="relative snap-start h-[calc(100svh-80px)] md:h-[calc(100svh-100px)] w-full max-w-md mx-auto bg-black rounded-lg overflow-hidden shadow-xl">
      <video
        ref={videoRef}
        src={video.video_url}
        loop
        muted={isMuted}
        playsInline
        className="w-full h-full object-cover"
        onClick={handleVideoClick}
      />

      {/* Main Overlay for UI elements */}
      <div
        className={cn(
          "absolute inset-0 flex flex-col text-white pointer-events-none", // pointer-events-none for overlay, specific children get pointer-events-auto
          // The main gradient is applied here, but the expanded caption will have its own stronger gradient.
          isCaptionExpanded && captionIsPotentiallyLong
            ? "justify-end" // When caption expanded, main content is at bottom
            : "justify-between p-4 bg-gradient-to-t from-black/50 via-transparent to-transparent",
        )}
      >
        {/* User Info - only show if caption is not expanded or not long */}
        {!(isCaptionExpanded && captionIsPotentiallyLong) && (
          <div className="flex items-center space-x-2 pointer-events-auto">
            <Avatar>
              <AvatarImage src={video.user_avatar || "/placeholder.svg"} alt={video.user_name} />
              <AvatarFallback>{video.user_name?.substring(0, 1).toUpperCase() || "U"}</AvatarFallback>
            </Avatar>
            <span className="font-semibold text-sm">{video.user_name || "Anonymous User"}</span>
          </div>
        )}

        {/* Caption and Hashtags Container */}
        <div
          className={cn(
            "relative transition-all duration-300 ease-in-out pointer-events-auto",
            isCaptionExpanded && captionIsPotentiallyLong
              ? "bg-gradient-to-t from-black/80 via-black/70 to-black/30 px-4 pt-16 pb-4 max-h-[60vh] flex flex-col" // Expanded state
              : "px-0 pt-0 pb-0", // Collapsed state (padding is from parent or none if parent changes)
          )}
          // Add onClick here if the whole area should toggle, otherwise it's on the <p>
        >
          {video.caption && (
            <p
              className={cn(
                "text-sm mb-1",
                captionIsPotentiallyLong ? "cursor-pointer" : "",
                isCaptionExpanded && captionIsPotentiallyLong ? "overflow-y-auto flex-grow" : "line-clamp-2", // line-clamp for collapsed
              )}
              onClick={captionIsPotentiallyLong ? toggleCaptionExpansion : undefined}
            >
              {displayedCaption}
              {!isCaptionExpanded && captionIsPotentiallyLong && (
                <span className="font-semibold hover:underline">more</span>
              )}
            </p>
          )}
          {/* Hashtags: show if caption not expanded, or if caption isn't long enough to be expandable */}
          {(!isCaptionExpanded || !captionIsPotentiallyLong) && video.hashtags && video.hashtags.length > 0 && (
            <p className="text-xs text-gray-300 mt-1">{video.hashtags.join(" ")}</p>
          )}
        </div>
      </div>

      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <Button
            variant="ghost"
            size="icon"
            onClick={togglePlay}
            className="text-white/80 hover:text-white h-20 w-20 pointer-events-auto"
          >
            <Play className="h-16 w-16" />
          </Button>
        </div>
      )}

      {/* Side Action Buttons */}
      <div className="absolute right-2 bottom-16 sm:bottom-20 flex flex-col space-y-3 sm:space-y-4 pointer-events-auto">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleMute}
          className="text-white bg-black/30 hover:bg-black/50 p-2 rounded-full"
        >
          {isMuted ? <VolumeX className="h-5 w-5 sm:h-6 sm:w-6" /> : <Volume2 className="h-5 w-5 sm:h-6 sm:w-6" />}
          <span className="sr-only">{isMuted ? "Unmute" : "Mute"}</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => e.stopPropagation()}
          className="text-white bg-black/30 hover:bg-black/50 p-2 rounded-full"
        >
          <Heart className="h-5 w-5 sm:h-6 sm:w-6" />
          <span className="sr-only">Like</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => e.stopPropagation()}
          className="text-white bg-black/30 hover:bg-black/50 p-2 rounded-full"
        >
          <MessageSquare className="h-5 w-5 sm:h-6 sm:w-6" />
          <span className="sr-only">Comment</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => e.stopPropagation()}
          className="text-white bg-black/30 hover:bg-black/50 p-2 rounded-full"
        >
          <Share2 className="h-5 w-5 sm:h-6 sm:w-6" />
          <span className="sr-only">Share</span>
        </Button>
        <Button
          onClick={handleRecommendClick}
          variant="outline"
          className="text-white bg-teal-500/80 hover:bg-teal-500 border-teal-500 hover:text-white p-2 rounded-full flex flex-col items-center h-auto"
        >
          <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 mb-0.5" />
          <span className="text-xs font-medium">Suggest</span>
        </Button>
      </div>
    </div>
  )
}

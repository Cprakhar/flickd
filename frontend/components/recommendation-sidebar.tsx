"use client"

import type React from "react"
import Image from "next/image"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { RecommendationData } from "@/lib/types"
import { X, ShoppingBag, Tag } from "lucide-react"
import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog"
import { Maximize } from "lucide-react"

interface RecommendationSidebarProps {
  isOpen: boolean
  onOpenChange: (isOpen: boolean) => void
  recommendations: RecommendationData | null
  isLoading: boolean
}

export function RecommendationSidebar({
  isOpen,
  onOpenChange,
  recommendations,
  isLoading,
}: RecommendationSidebarProps) {
  const [enlargedImageSrc, setEnlargedImageSrc] = useState<string | null>(null)
  const [isImageModalOpen, setIsImageModalOpen] = useState(false)

  const handleImageClick = (imageUrl: string) => {
    setEnlargedImageSrc(imageUrl)
    setIsImageModalOpen(true)
  }


  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-md p-0 flex flex-col">
        <SheetHeader className="p-6 pb-2 border-b">
          <SheetTitle className="flex items-center">
            <ShoppingBag className="mr-2 h-5 w-5 text-teal-500" />
            Style Suggestions
          </SheetTitle>
          {recommendations && !isLoading && <SheetDescription>For video: {recommendations.video_id}</SheetDescription>}
        </SheetHeader>

        <ScrollArea className="flex-grow">
          <div className="p-6">
            {isLoading && (
              <div className="flex flex-col items-center justify-center h-full">
                <Loader2 className="h-12 w-12 animate-spin text-teal-500 mb-4" />
                <p className="text-muted-foreground">Finding recommendations...</p>
              </div>
            )}
            {!isLoading && recommendations && (
              <>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2 flex items-center">
                    <Tag className="mr-2 h-5 w-5 text-purple-500" />
                    Vibes
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {recommendations.vibes.map((vibe) => (
                      <Badge key={vibe} variant="secondary" className="text-sm bg-purple-100 text-purple-700">
                        {vibe}
                      </Badge>
                    ))}
                    {recommendations.vibes.length === 0 && (
                      <p className="text-sm text-muted-foreground">No vibes detected.</p>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Recommended Products</h3>
                  {recommendations.products.length === 0 && (
                    <p className="text-sm text-muted-foreground">No products to recommend for this video yet.</p>
                  )}
                  <div className="space-y-4">
                    {recommendations.products.map((product) => (
                      <div
                        key={product.matched_product_id}
                        className="flex items-start space-x-3 p-3 border rounded-lg bg-card relative"
                      >
                        <div
                          className="relative group cursor-pointer"
                          onClick={() => handleImageClick(product.image_url || "/placeholder.svg")}
                        >
                          <Image
                            src={product.image_url || "/placeholder.svg"}
                            alt={product.title || product.type || "Product"}
                            width={80}
                            height={100}
                            className="rounded-md object-cover aspect-[4/5]"
                          />
                          <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-md">
                            <Maximize className="h-6 w-6 text-white" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{product.title || product.type}</h4>
                          <p className="text-sm text-muted-foreground capitalize">
                            {product.type} - {product.color}
                          </p>
                          <div className="mt-8">
                            <Badge variant={product.match_type === "exact" ? "default" : "outline"} className="text-xs">
                              {product.match_type === "exact" ? "Exact Match" : "Similar Item"}
                            </Badge>
                          </div>
                        </div>
                        {typeof product.confidence === "number" && (
                          <span
                            className="absolute bottom-2 right-2 text-xs text-white px-2 py-0.5 rounded font-semibold shadow"
                            style={{
                              background: product.confidence >= 0.85
                                ? 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)' // green
                                : product.confidence >= 0.7
                                ? 'linear-gradient(90deg, #facc15 0%, #eab308 100%)' // yellow
                                : 'linear-gradient(90deg, #ef4444 0%, #b91c1c 100%)' // red
                            }}
                          >
                            {product.confidence.toFixed(2)}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            {!isLoading && !recommendations && (
              <div className="text-center text-muted-foreground py-10">
                <p>Click "✨ Suggest" on a video to see recommendations here.</p>
              </div>
            )}
          </div>
        </ScrollArea>

        {enlargedImageSrc && (
          <Dialog open={isImageModalOpen} onOpenChange={setIsImageModalOpen}>
            <DialogContent className="sm:max-w-[80vw] md:max-w-[60vw] lg:max-w-[50vw] xl:max-w-[40vw] p-2 bg-background">
              <DialogHeader className="p-0">
                <DialogTitle className="sr-only">Enlarged Product Image</DialogTitle>
                <DialogClose>
                  <span className="sr-only">Close</span>
                </DialogClose>
              </DialogHeader>
              <div className="flex justify-center items-center max-h-[80vh]">
                <Image
                  src={enlargedImageSrc || "/placeholder.svg"}
                  alt="Enlarged product"
                  width={800}
                  height={1000}
                  className="rounded-md object-contain max-w-full max-h-[75vh]"
                  style={{ width: "auto", height: "auto" }}
                />
              </div>
            </DialogContent>
          </Dialog>
        )}
        
        {!isImageModalOpen && (
          <SheetFooter className="p-6 pt-2 border-t">
            <SheetClose asChild>
              <Button variant="outline" className="w-full">
                <X className="mr-2 h-4 w-4" /> Close
              </Button>
            </SheetClose>
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
}

// Helper component for loading state in sidebar
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

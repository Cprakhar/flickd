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
                    {/* {recommendations.vibes.map((vibe) => (
                      <Badge key={vibe} variant="secondary" className="text-sm bg-purple-100 text-purple-700">
                        {vibe}
                      </Badge>
                    ))}
                    {recommendations.vibes.length === 0 && (
                      <p className="text-sm text-muted-foreground">No vibes detected.</p>
                    )} */}
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
                        className="flex items-start space-x-3 p-3 border rounded-lg bg-card"
                      >
                        <Image
                          src={product.image_url || "/placeholder.svg"}
                          alt={product.title || product.type || "Product"}
                          width={80}
                          height={100}
                          className="rounded-md object-cover aspect-[4/5]"
                        />
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{product.title || product.type}</h4>
                          <p className="text-xs text-muted-foreground capitalize">
                            {product.type} - {product.color}
                          </p>
                          <div className="mt-1">
                            <Badge variant={product.match_type === "exact" ? "default" : "outline"} className="text-xs">
                              {product.match_type === "exact" ? "Exact Match" : "Similar Item"}
                            </Badge>
                          </div>
                        </div>
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

        <SheetFooter className="p-6 pt-2 border-t">
          <SheetClose asChild>
            <Button variant="outline" className="w-full">
              <X className="mr-2 h-4 w-4" /> Close
            </Button>
          </SheetClose>
        </SheetFooter>
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

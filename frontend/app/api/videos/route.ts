import { NextResponse } from "next/server"
import type { Video, VideosApiResponse } from "@/lib/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const allVideos: Video[] = [
  {
    video_id: "reel_001",
    video_url: `${API_URL}/videos/reel_001.mp4`,
    caption: `We started with a feeling.
              Now it has a name.

              This is Beyond The Curve.
              Not a trend. Not a label.

              A new standard, built from scratch, shaped by every woman who was told to wait.
              `,
    hashtags: [],
    user_name: "user123",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
  {
    video_id: "reel_002",
    video_url: `${API_URL}/videos/reel_002.mp4`,
    caption: `Sunkissed Summer has landed.
              Think golden hour, every hour.

              Easy silhouettes. Bare shoulders. Dresses that breathe.

              Made for holiday glow, even if you’re just stepping out for coffee.   
              `,
    hashtags: [],
    user_name: "dreamer_z",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
  {
    video_id: "reel_003",
    video_url: `${API_URL}/videos/reel_003.mp4`,
    caption: `✨ Comment “LINK” and I'll DM you the details! 🤍 GRWM in this easy-breezy cotton vest + skirt set — made in linen, made for summer! 🌞`,
    hashtags: ["#GRWM", "#LinenSet", "#SummerOutfit", "#CoOrdSet", "#OOTDIndia", "#GRWMReel"],
    user_name: "explorer_gal",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
  {
    video_id: "reel_004",
    video_url: `${API_URL}/videos/reel_004.mp4`,
    caption: `Ofcourse I'll get you flowers 🙆🏻‍♀️🙂‍↕️

              Spinning into summer with my favorite @virgio.official dress, you like it too? I got you girlie, comment ‘Link’ and I will slide into your dms with the link 🤜🤛

              Use code 'SUKRUTIAIRI' and save some extra 💸

              Location- @roasterycoffeehouseindia 📍Noida`,
    hashtags: ["#grwm", "#summer", "#summerfit", "#dress", "#date", "#datedress", "#outfit", "#fashion", "#outﬁtinspo"],
    user_name: "wanderlust_x",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
  {
    video_id: "reel_005",
    video_url: `${API_URL}/videos/reel_005.mp4`,
    caption: `Golden hour, all day long. ☀️

              Meet Sunkissed Summer, dresses that feel like a vacation, even when you're not on one.

              Lightweight. Bold. Breathable. Made for days when the sun doesn't clock out.

              This is your wear-everywhere summer wardrobe.`,
    hashtags: [],
    user_name: "joker_01",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
  {
    video_id: "reel_006",
    video_url: `${API_URL}/videos/reel_006.mp4`,
    caption: `She's an advocate, co-founder of a bakery and a model, a Vogue Model. Zainika was born with down-syndrome but that never stopped her from chasing her passion and dreams. She's wearing Our Rani Udaymati Collection, and it suits her perfectly- the statement designs bring out her confident personality. She's strong, she's passionate and her main message to everyone out there is plain and simple- be kind!
              Featuring: 
              Chaukhdi Necklace in Oxidised 925 Silver
              Kumbha Jhumki Earrings in Oxidised 925 Silver
              Rudra Ring in Oxidised 925 Silver
              Jyamitiya Stackable Rings in Oxidised 925 Silver
              Kumbha Bracelet in Oxidised 925 Silver`,
    hashtags: ["#Shaya", "#ShayaByCaratlane", "#SoShaya", "#SoShaya", "#Virgio", "#DownSyndromeAdvocate", "#WomenEmpowerment", "#BodyPositivity"],
    user_name: "so_shaya",
    user_avatar: "/placeholder.svg?width=40&height=40",
  },
]

const PAGE_SIZE = 3

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const page = Number.parseInt(searchParams.get("page") || "1", 10)

  const start = (page - 1) * PAGE_SIZE
  const end = start + PAGE_SIZE
  const paginatedVideos = allVideos.slice(start, end)

  const response: VideosApiResponse = {
    status: "success",
    data: paginatedVideos,
    next_page: end < allVideos.length ? page + 1 : null,
  }

  return NextResponse.json(response)
}

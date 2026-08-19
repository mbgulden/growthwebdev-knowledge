---
type: Standard
title: Schema Templates for Windward Oahu Location Pages
description: JSON-LD templates for LocalBusiness/TravelAgency, Product/Service, HowTo, FAQPage.
tags: [aot, seo, geo, ai-seo, migrated-from-existing]
timestamp: 2026-06-19T12:28:24Z
linear_issue: GRO-795
git_path: okf/strategy/schema-templates.md
status: current
migrated_from: /home/ubuntu/work/seo-strategy-gro-795/schema_templates.md
visibility: private
resource: okf/hubs/active-oahu/seo/strategy/schema-templates.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Schema Templates for Windward Oahu Location Pages

This document provides valid, copy-pasteable JSON-LD schema templates for the three locations. Every guide page must implement these schemas to maximize visibility in Google AI Overviews and traditional SERPs.

---

## 1. LocalBusiness / TravelAgency Schema (Kailua Storefront)

This schema establishes our physical storefront at **134B Hamakua Dr** as the central entity. Place this in the head of all location and guide pages.

```json
{
  "@context": "https://schema.org",
  "@type": "TravelAgency",
  "@id": "https://activeoahutours.com/#storefront",
  "name": "Active Oahu Tours",
  "url": "https://activeoahutours.com",
  "logo": "https://activeoahutours.com/assets/images/logo.png",
  "image": "https://activeoahutours.com/assets/images/storefront.jpg",
  "description": "Premium self-guided kayak rentals, e-bike rentals, beach gear, and guided adventures on Windward Oahu.",
  "telephone": "+1-808-498-1894",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "134B Hamakua Dr",
    "addressLocality": "Kailua",
    "addressRegion": "HI",
    "postalCode": "96734",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 21.391694,
    "longitude": -157.747194
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
      ],
      "opens": "07:00",
      "closes": "17:00"
    }
  ],
  "areaServed": [
    {
      "@type": "AdministrativeArea",
      "name": "Oahu"
    },
    {
      "@type": "AdministrativeArea",
      "name": "Kailua"
    },
    {
      "@type": "AdministrativeArea",
      "name": "Lanikai"
    },
    {
      "@type": "AdministrativeArea",
      "name": "Waimanalo"
    }
  ],
  "sameAs": [
    "https://www.facebook.com/activeoahutours",
    "https://www.instagram.com/activeoahutours",
    "https://www.yelp.com/biz/active-oahu-tours-kailua-2",
    "https://www.tripadvisor.com/Attraction_Review-g60607-d4778712-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html"
  ]
}
```

---

## 2. Product & Service Schema (Kailua/Lanikai Kayak Rental)

Used on `/rentals/kayak-rentals/` or pages detailing specific packages to secure Rich Product Snippets (price, availability).

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://activeoahutours.com/rentals/kayak-rentals/#product",
  "name": "Tandem Kayak Rental (Self-Guided)",
  "image": "https://activeoahutours.com/assets/images/tandem-kayak.jpg",
  "description": "Premium 2-person ocean kayak rentals for exploring Kailua Bay, Popoia Island, and the Mokulua Islands. Includes paddles, life vests, dry bags, and soft car racks.",
  "brand": {
    "@type": "Brand",
    "name": "Active Oahu Tours"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://activeoahutours.com/rentals/kayak-rentals/",
    "priceCurrency": "USD",
    "price": "79.00",
    "priceValidUntil": "2027-12-31",
    "itemCondition": "https://schema.org/NewCondition",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "LocalBusiness",
      "name": "Active Oahu Tours"
    }
  }
}
```

---

## 3. HowTo Schema (e.g., How to Park legally at Lanikai Beach)

Highly structured data for answering parking and access queries in Google's AI Overviews and Rich Results.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Find Legal Parking at Lanikai Beach",
  "description": "A step-by-step local guide to finding legal parking at Lanikai Beach without getting a $200 ticket or towed.",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": "0.00"
  },
  "totalTime": "PT15M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Arrive early",
      "text": "Arrive before 8:00 AM on weekdays or 7:00 AM on weekends to secure a spot in the primary legal parking areas.",
      "url": "https://activeoahutours.com/guides/lanikai-beach-parking/#step1",
      "image": "https://activeoahutours.com/assets/images/parking-early.jpg"
    },
    {
      "@type": "HowToStep",
      "name": "Park at Kailua Beach Park",
      "text": "Park in the free public lot at Kailua Beach Park (526 Kawailoa Road). This is the safest legal option with 300+ stalls and full restroom facilities.",
      "url": "https://activeoahutours.com/guides/lanikai-beach-parking/#step2",
      "image": "https://activeoahutours.com/assets/images/kailua-parking-lot.jpg"
    },
    {
      "@type": "HowToStep",
      "name": "Walk or bike into Lanikai",
      "text": "Walk or ride an electric bike 1 mile south along the flat paved path from Kailua Beach Park to the Lanikai beach access points.",
      "url": "https://activeoahutours.com/guides/lanikai-beach-parking/#step3",
      "image": "https://activeoahutours.com/assets/images/walk-to-lanikai.jpg"
    },
    {
      "@type": "HowToStep",
      "name": "Check street signs and markings",
      "text": "If attempting to park on Lanikai's residential streets (Aalapapa or Mokulua Drive), ensure your tires are completely off the paved roadway, you are not blocking any driveways, and you are not parked within 4 feet of fire hydrants or on bike lanes.",
      "url": "https://activeoahutours.com/guides/lanikai-beach-parking/#step4",
      "image": "https://activeoahutours.com/assets/images/lanikai-signs.jpg"
    }
  ]
}
```

---

## 4. FAQPage Schema (Template for Waimanalo Beach Guide)

This schema formats the Q&A blocks to make them highly extractable for search bots.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is there parking at Waimanalo Beach Park?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Waimanalo Beach Park has a large, free paved parking lot located directly off Kalanianaole Highway. Unlike Lanikai, parking here is abundant and rarely fills up completely, except during peak summer holiday weekends."
      }
    },
    {
      "@type": "Question",
      "name": "Is Waimanalo Beach safe for swimming?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Waimanalo Beach is safe for swimming during calm summer months (May to September) when the shore break is minimal. However, it is more exposed to open ocean swells than Kailua, resulting in stronger currents. Swim near the lifeguard towers, and avoid entering the water during winter swell events or high winds."
      }
    },
    {
      "@type": "Question",
      "name": "Can I have kayak rentals delivered to Waimanalo Beach?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Commercial delivery of water sports equipment is strictly prohibited at Waimanalo Beach by DLNR regulations. To kayak in Waimanalo, you must rent equipment directly from our Kailua storefront at 134B Hamakua Dr and transport it to the launch point on your own vehicle using the soft racks we provide."
      }
    }
  ]
}
```

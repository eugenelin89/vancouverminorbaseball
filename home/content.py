"""Static content data for the Vancouver Minor site."""

HERO = {
    "title": "Baseball for Every Vancouver Athlete",
    "eyebrow": "Home of the VMB Expos",
    "paragraphs": [
        "Since 1999, Vancouver Minor Baseball has welcomed players and families into an inclusive, competitive, and community-first experience.",
        "Certified coaches, transparent communication, and elite development pathways help every athlete take the next step—on and off the diamond.",
    ],
    "cta_primary": {"label": "Register for 2026", "url": "/registration/"},
    "cta_secondary": {"label": "Explore Our Divisions", "url": "/#divisions"},
    "hero_support": "Tryouts begin March 1 · Opening Day April 18",
}

VALUE_PROPOSITIONS = [
    {
        "title": "Player-First Coaching",
        "description": "NCCP-certified coaches deliver skill progressions, video review, and individualized development plans at every level.",
        "icon": "🎯",
    },
    {
        "title": "Inclusive Community",
        "description": "Financial assistance, equipment loaner programs, and mentorship initiatives ensure every athlete feels welcome.",
        "icon": "🤝",
    },
    {
        "title": "Competitive Pathways",
        "description": "Tiered teams (A, AA, AAA) compete across BC and the Pacific Northwest, with exposure to collegiate recruiters and scouts.",
        "icon": "🏆",
    },
]

DIVISION_SUMMARIES = [
    {
        "name": "13U Pee Wee",
        "ages": "Ages 11–13",
        "training_focus": "Fundamentals, position rotations, and confidence building with weekly skill labs.",
        "practice_days": "Practices Tue/Thu · Games Sat",
        "coach": "Head Coach: Jamie Singh",
    },
    {
        "name": "15U Bantam",
        "ages": "Ages 14–15",
        "training_focus": "Advanced defensive systems, pitching development, and sport performance workshops.",
        "practice_days": "Practices Mon/Wed · Games Fri",
        "coach": "Head Coach: Carla Mendes",
    },
    {
        "name": "18U Midget",
        "ages": "Ages 16–18",
        "training_focus": "Showcase tournaments, collegiate preparation, leadership, and sport science support.",
        "practice_days": "Practices Tue/Thu/Sun",
        "coach": "Head Coach: Andre Delgado",
    },
    {
        "name": "26U Junior Men's",
        "ages": "Ages 19–26",
        "training_focus": "High-performance competition, strength & conditioning, and mentorship for younger teams.",
        "practice_days": "Practices Wed/Fri · Games Sun",
        "coach": "Head Coach: Priya Patel",
    },
]

TESTIMONIALS = [
    {
        "quote": "Our son found a second family with the Expos. His pitching velocity jumped 6 mph and his confidence soared.",
        "attribution": "— Allison W., 15U parent",
    },
    {
        "quote": "The coaching staff goes beyond drills—they teach accountability, leadership, and how to compete the right way.",
        "attribution": "— Coach Marcus, 18U assistant",
    },
    {
        "quote": "Joining Vancouver Minor Baseball helped me earn a college roster spot. The exposure and support are unmatched.",
        "attribution": "— Riley N., 26U alum",
    },
]

GALLERY = [
    {
        "image": "images/achievement-09.png",
        "alt": "VMB players celebrate a walk-off win at dusk",
        "caption": "Walk-off celebrations at Nanaimo Park",
    },
    {
        "image": "images/achievement-10.png",
        "alt": "13U Expos player stretching for an out at first base",
        "caption": "13U Expos flashing the leather",
    },
    {
        "image": "images/achievement-08.png",
        "alt": "26U Expos lineup during national anthem",
        "caption": "Junior Men's squad ready for first pitch",
    },
]

KEY_DATES = [
    {"label": "Winter Skills Clinics", "date": "Saturdays · January 10 – February 21"},
    {"label": "Open Tryouts", "date": "March 1–3 · Nanaimo Park"},
    {"label": "Season Kickoff", "date": "April 18 · Opening Night"},
    {"label": "Community Day & BBQ", "date": "June 7 · John Hendry Park"},
]

CONTACT_INFO = {
    "email": "registrar@vmbaseball.ca",
    "phone": "604-555-0199",
    "address": "Nanaimo Park Diamond, 2390 E 46th Ave, Vancouver, BC",
    "map_url": "https://maps.app.goo.gl/5xHj9hNxKD9VMBPark",
    "office_hours": "Mon–Fri · 9am – 4pm",
}

LEAD_CAPTURE = {
    "title": "Get season updates",
    "description": "Join the mailing list for registration reminders, tryout details, and community events.",
    "placeholder": "Email address",
    "button": "Notify Me",
}

PROGRAMS_PAGE = {
    "title": "Programs",
    "tagline": "From Pee Wee to Junior Men's",
    "hero_image": "images/programs-hero.jpg",
    "hero_image_label": "programs-hero.jpg",
    "intro": "We offer divisions for players aged 11 through 25:",
    "divisions": [
        "Pee Wee (11–12 years old)",
        "Bantam (13–14 years old)",
        "Midget (15–17 years old)",
        "Junior Men's (18–25 years old)",
    ],
    "closing": (
        "Players participate within their appropriate age category. Movement to an older division may be permitted "
        "only when a player demonstrates the skill, maturity, and readiness required to succeed at the next level."
    ),
}

REGISTRATION_PAGE = {
    "title": "Registration",
    "eyebrow": "Join Vancouver Minor Baseball",
    "tagline": "Registration for the 2026 season begins December 1.",
    "hero_image": "images/registration-hero.jpg",
    "hero_image_label": "registration-hero.jpg",
    "intro": (
        "Geographical boundaries: Vancouver Minor Baseball welcomes athletes who reside within the City of Vancouver. "
        "Families outside of the city limits are invited to apply with VMB once a release from their home association has been granted."
    ),
    "sections": [
        {
            "title": "Age Eligibility",
            "body": (
                "VMB programs are offered at the 13U, 15U, 18U, and 26U divisions. Players must be the stated age or "
                "younger as of December 31, 2025. Division requirements will be reaffirmed for the 2026 season when registration opens."
            ),
        },
        {
            "title": "Little League Pathway",
            "body": (
                "Players who remain Little League eligible—12 years old or younger as of August 31 of the current calendar year—"
                "are encouraged to continue with their local Little League club before transitioning to Vancouver Minor Baseball. "
                "Links to each Vancouver-area Little League will be provided below to help families connect directly."
            ),
        },
        {
            "title": "Next Steps",
            "body": (
                "Our registration team is finalizing season logistics, fee schedules, and key dates. "
                "Online registration will open on December 1 for the 2026 season—check back for the live form or join the mailing list to receive launch reminders."
            ),
        },
    ],
    "divisions": ["13U", "15U", "18U", "26U"],
}

NAVIGATION = [
    {"label": "Home", "url": "/", "children": []},
    {"label": "About", "url": "/#about", "children": []},
    {"label": "Divisions", "url": "/#divisions", "children": []},
    {"label": "Schedule", "url": "/#schedule", "children": []},
    {"label": "Gallery", "url": "/#gallery", "children": []},
    {
        "label": "Registration",
        "url": "/registration/",
        "children": [],
    },
    {
        "label": "Contact",
        "url": "/#contact",
        "children": [],
    },
    {
        "label": "Register",
        "url": "/registration/",
        "children": [],
        "is_cta": True,
    },
]

SOCIAL_LINKS = [
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/vancouverminorbaseball",
        "icon": "facebook",
        "icon_path": "icons/facebook.svg",
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/vanminor_baseball/",
        "icon": "instagram",
        "icon_path": "icons/instagram.svg",
    },
]

ACHIEVEMENTS = [
    {
        "slug": "achievement-01",
        "title": "15U AA Provincial Champions 2025\nVMB Expos 15U AA Blue",
        "image_alt": "Prov-Team-8354",
    },
    {
        "slug": "achievement-02",
        "title": "13U AAA GSL Summer Slam Premier Sports Tournament Champions 2025 - Everett, Washington, USA",
        "image_alt": "SummerSlam",
    },
    {
        "slug": "achievement-05",
        "title": "Steven Dodd Memorial Tournament Champions 2025\nVMB Expos 15U AA Blue",
        "image_alt": "Resize_PXL_20250701_002711715",
    },
    {
        "slug": "achievement-07",
        "title": "Ross Tournament Champions 2025\nVMB Expos 15U AA Blue",
        "image_alt": "15U-AA-Team-Blue-Ross-Tournament-Champions-2025-e1754637283675",
    },
    {
        "slug": "achievement-11",
        "title": "13U AA - Jevon Clarke Memorial Tournament Second Place Finish",
        "image_alt": "13U AA Jevon Clark",
    },
    {
        "slug": "achievement-12",
        "title": "15U A Notable - Battle At The Barn Ladner 2025 Third Place Finish",
        "image_alt": "15U A Notable - Third Place Finish Battle At The Barn Ladner 2025",
    },
]

FOOTER_TEXT = "© 2025 Vancouver Minor Baseball"

"""Static content data for the Vancouver Minor site."""

HERO = {
    "title": "Baseball for Every Season in Vancouver",
    "eyebrow": "Home of the VMB Expos",
    "paragraphs": [
        "Vancouver Minor Baseball has proudly been affiliated with BC Minor Baseball Association since 1999.",
        "We provide an inclusive pathway where athletes learn the game, grow as leaders, and compete at the highest community levels in British Columbia.",
    ],
    "highlights": [
        "Player development programs for ages 11–25",
        "Certified coaching staff, trainers, and mentors",
        "Community-first culture rooted in sportsmanship",
    ],
    "cta": {"label": "Register for 2026", "url": "/registration/"},
    "secondary_cta": {"label": "Explore Programs", "url": "/programs/"},
    "hero_image": "images/hero-banner.jpg",
    "hero_image_alt": "VMB Expos players celebrating a game-winning slide at home plate.",
}

ABOUT = {
    "eyebrow": "About Vancouver Minor Baseball",
    "title": "Rooted in Community Since 1999",
    "mission": (
        "Vancouver Minor Baseball Association is a volunteer-driven organization committed to making baseball accessible, safe, and inspiring for every athlete across Vancouver."
    ),
    "history": (
        "From a handful of neighbourhood teams to a city-wide club, VMB has helped thousands of players discover their love of the game. We invest in professional coaching, leadership training, and year-round development to keep athletes engaged."
    ),
    "pillars": [
        {
            "title": "Player Development",
            "description": "Progressive training plans, strength and conditioning support, and dedicated pitching and catching instruction for every division.",
        },
        {
            "title": "Belonging & Inclusion",
            "description": "Financial assistance programs, equipment libraries, and mentorship pairings ensure every athlete can take the field with confidence.",
        },
        {
            "title": "Community Impact",
            "description": "Players volunteer at local schools, support neighbourhood cleanups, and represent Vancouver at BC Minor and Baseball Canada events.",
        },
    ],
    "stats": [
        {"label": "Members in 2025", "value": "320+"},
        {"label": "Certified Coaches", "value": "45"},
        {"label": "Championships Since 2018", "value": "11"},
    ],
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
    {"label": "Why Join", "url": "/#why-join", "children": []},
    {"label": "Contact", "url": "/#contact", "children": []},
    {"label": "Registration", "url": "/registration/", "children": [], "is_cta": True},
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

VALUE_PROPS = [
    {
        "title": "Experienced Coaches",
        "body": "NCCP-certified coaches build fundamentals through weekly skills labs, video review, and progress check-ins with families.",
    },
    {
        "title": "Player Pathways",
        "body": "Opportunities range from recreational leagues to tournament travel teams with exposure to college scouts and high-performance partners.",
    },
    {
        "title": "Whole Athlete Support",
        "body": "Mental performance workshops, athletic therapy partnerships, and leadership programs develop confident, resilient teammates.",
    },
]

DIVISION_SUMMARIES = [
    {
        "name": "13U Pee Wee",
        "ages": "Ages 11–13",
        "summary": "Entry to full-sized baseball diamonds with a focus on fundamentals, confidence, and game awareness.",
        "training": "Two practices and one weekend game each week from April through August.",
        "coach": "Lead Coach: Jamie Chen",
    },
    {
        "name": "15U Bantam",
        "ages": "Ages 13–15",
        "summary": "Athletes refine positional play, speed training, and strategy against top BC Minor competition.",
        "training": "Three field sessions plus strength and conditioning support at our partner facility.",
        "coach": "Lead Coach: Marco Ortiz",
    },
    {
        "name": "18U Midget",
        "ages": "Ages 15–18",
        "summary": "High-performance reps with showcase tournaments, college prep advising, and leadership mentoring.",
        "training": "Four combined practices or games weekly including travel tournaments across the Pacific Northwest.",
        "coach": "Lead Coach: Serena Watanabe",
    },
    {
        "name": "26U Junior Men's",
        "ages": "Ages 19–26",
        "summary": "Competitive men’s baseball blending university athletes and alumni returning to the diamond.",
        "training": "Spring training camp, regular season double-headers, and fall development scrimmages.",
        "coach": "Player-Coach: Devon Mitchell",
    },
]

KEY_DATES = [
    {
        "date": "December 1, 2025",
        "title": "2026 Registration Opens",
        "description": "Secure your roster spot early and receive winter training invites.",
    },
    {
        "date": "January 12, 2026",
        "title": "Winter Workouts Begin",
        "description": "Indoor skill sessions at Vancouver College Fieldhouse for all divisions.",
    },
    {
        "date": "March 7–8, 2026",
        "title": "Preseason Evaluation Weekend",
        "description": "On-field assessments and team placements at Hillcrest Park."
    },
]

TESTIMONIALS = [
    {
        "quote": "My daughter’s confidence skyrocketed thanks to the mentorship she received at VMB. Coaches celebrate every win and teach through every challenge.",
        "attribution": "Parent of a 13U player",
    },
    {
        "quote": "The Junior Men's program kept me connected to the game while studying at UBC. Practices are competitive, fun, and super organized.",
        "attribution": "Evan, 26U infielder",
    },
    {
        "quote": "We love the community feel—families show up, volunteers are amazing, and the kids leave the park smiling every time.",
        "attribution": "Sharon, team manager",
    },
]

GALLERY = [
    {
        "image": "images/achievement-01.png",
        "alt": "15U AA VMB Expos holding the provincial championship banner.",
        "caption": "15U AA Provincial Champions",
    },
    {
        "image": "images/achievement-02.png",
        "alt": "13U Expos celebrating a tournament win in Everett, Washington.",
        "caption": "13U Summer Slam Winners",
    },
    {
        "image": "images/achievement-07.png",
        "alt": "VMB 15U Blue team gathered on the mound with trophies.",
        "caption": "Ross Tournament Champions",
    },
    {
        "image": "images/achievement-11.png",
        "alt": "13U Expos posing with silver medals at Jevon Clarke Memorial Tournament.",
        "caption": "Jevon Clarke Finalists",
    },
]

FAQ_ITEMS = [
    {
        "question": "What equipment do players need?",
        "answer": "Players require a glove, cleats, and batting helmet. VMB supplies team bats, catcher's gear, and uniforms. Our equipment library can assist with anything else needed.",
    },
    {
        "question": "How much does a season cost?",
        "answer": "2026 fees range from $395–$875 depending on the division. Financial assistance is available through KidSport, Jumpstart, and VMB subsidies—contact us for details.",
    },
    {
        "question": "Where do teams practice and play?",
        "answer": "Home diamonds include Hillcrest Park, Trout Lake, and Vancouver College. Travel teams compete across the Lower Mainland and Pacific Northwest tournaments.",
    },
    {
        "question": "Who can I contact about volunteering?",
        "answer": "Email volunteers@vancouverminor.com to learn about coaching, scorekeeping, and event support opportunities. We provide training for every role.",
    },
]

CONTACT_INFO = {
    "email": "info@vancouverminor.com",
    "phone": "604-555-0199",
    "phone_href": "+16045550199",
    "address": "Hillcrest Park Diamond – 4501 Clancy Loranger Way, Vancouver, BC",
    "map_url": "https://maps.google.com/?q=Hillcrest+Park+Baseball+Diamond+Vancouver",
    "office_hours": "Mon–Fri 9:00 a.m.–4:00 p.m.",
    "mailing_list_url": "https://vancouverminor.com/subscribe",
}

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

FOOTER_TEXT = "© 2025 Vancouver Minor Baseball Association. All rights reserved."

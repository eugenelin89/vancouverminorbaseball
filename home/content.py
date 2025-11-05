"""Static content data for the Vancouver Minor site."""

HERO = {
    "title": "Welcome to Vancouver Minor Baseball",
    "eyebrow": "Home of the VMB Expos",
    "paragraphs": [
        "Vancouver Minor Baseball has proudly been affiliated with BC Minor Baseball Association since 1999. We provide a positive and structured environment for youth and young adults to learn, develop, and compete in the game of baseball.",
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
    {
        "label": "Registration",
        "url": "/registration/",
        "children": [],
    },
    {
        "label": "Programs",
        "url": "/programs/",
        "children": [
            {
                "label": "13U",
                "url": "/13u/",
                "children": [
                    {"label": "About 13U", "url": "/13u/", "children": []},
                    {"label": "13U A", "url": "/13u/13u-a/", "children": []},
                    {"label": "13U AA", "url": "/13u/13u-aa/", "children": []},
                    {"label": "13U AAA", "url": "/13u/13u-aaa/", "children": []},
                ],
            },
            {
                "label": "15U",
                "url": "/15u/",
                "children": [
                    {"label": "About 15U", "url": "/15u/", "children": []},
                    {"label": "15U A", "url": "/15u/15u-a/", "children": []},
                    {
                        "label": "15U AA",
                        "url": "/15u/15u-aa/",
                        "children": [
                            {"label": "15U AA Blue 'Expos'", "url": "/15u-aa-blue-expos/", "children": []},
                            {"label": "15U AA Red 'Expos'", "url": "/15u-aa-red-expos/", "children": []},
                        ],
                    },
                    {"label": "15U AAA", "url": "/15u/15u-aaa/", "children": []},
                ],
            },
            {
                "label": "18U",
                "url": "/18u/",
                "children": [
                    {"label": "About 18U", "url": "/18u/", "children": []},
                    {"label": "18U AA", "url": "/18u/18u-aa/", "children": []},
                    {"label": "18U AAA", "url": "/18u/18u-aaa/", "children": []},
                ],
            },
            {
                "label": "26U",
                "url": "/26u/",
                "children": [
                    {"label": "About 26U", "url": "/26u/", "children": []},
                    {"label": "26U 'Expos'", "url": "/26u-expos/", "children": []},
                    {"label": "26U 'Expos Red'", "url": "/26u-expos-red/", "children": []},
                ],
            },
            {"label": "All-Girls Baseball", "url": "/girls-baseball/", "children": []},
        ],
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

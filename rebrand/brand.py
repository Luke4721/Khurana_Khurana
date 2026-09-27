#!/usr/bin/env python3
"""Palette + identity pairs for the K&K rebrand (engine31-compatible).
Values use a RAW ampersand: React does NOT HTML-decode flight strings, so
&amp; in flight would render literally and mismatch the SSR markup."""

# indigo navies -> warm charcoal; mid-navies -> K&K maroon/slate family
PALETTE = [
    ("#000321", "#0d0a0c"),
    ("#000218", "#0b090a"),
    ("#000214", "#0a0808"),
    ("#05071c", "#120d0f"),
    ("#010320", "#140e10"),
    ("#0a1240", "#2b140f"),
    ("#10234f", "#3a1a12"),
    ("#000020", "#0d0a0c"),
]

def identity_pairs():
    """Global identity replacements (order matters: longest first)."""
    A = "&"
    return [
        # meta
        ("Momento Legal — Law. Strategy. Timing. | Momento Legal",
         f"Khurana {A} Khurana — Advocates and IP Attorneys | Khurana {A} Khurana"),
        ("An independent legal and advisory platform providing strategic counsel to companies, investors, and entrepreneurs",
         "A full-service intellectual property and corporate law firm providing strategic counsel to companies, innovators, and entrepreneurs"),
        # brand names (longest forms first)
        ("Momento Legal Partners", f"Khurana {A} Khurana"),
        ("MOMENTO LEGAL", f"KHURANA {A} KHURANA"),
        ("Momento Legal", f"Khurana {A} Khurana"),
        ("MOMENTO", f"KHURANA {A} KHURANA"),
        ("momentolegal.com", "khuranaandkhurana.com"),
        ("Momento", f"Khurana {A} Khurana"),
        # hero
        ("The Moment of Precision", "Rendering Sage Legal Advice"),
        ("Law. Strategy. Timing.", "Law. Strategy. Precision."),
        ("The moment of precision", "Rendering sage legal advice"),
        # email
        ("info@momentolegal.com", "info@khuranaandkhurana.com"),
        # socials
        ("https://www.instagram.com/momentolegal/", "https://www.instagram.com/khuranaandkhurana/"),
        ("https://www.linkedin.com/company/momento-legal-partners/", "https://www.linkedin.com/company/khurana-&-khurana-advocates-and-ip-attorneys"),
        ("instagram.com/momentolegal", "instagram.com/khuranaandkhurana"),
        ("momento-legal-partners", "khurana-&-khurana-advocates-and-ip-attorneys"),
    ]

# strings that must NOT exist anywhere after migration (QA)
FORBIDDEN = [
    "momentolegal", "Momento Legal", "MOMENTO LEGAL", "MOMENTO",
    "The Moment of Precision", "Law. Strategy. Timing.",
    "info@momentolegal.com", "istcode", "Istcode", "awwwards", "Awwwards",
]

if __name__ == "__main__":
    print("palette:", len(PALETTE), "identity:", len(identity_pairs()), "forbidden:", len(FORBIDDEN))

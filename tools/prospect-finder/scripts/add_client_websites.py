#!/usr/bin/env python3
"""Add website URLs to existing clients."""

import sqlite3

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"

# Known client websites
WEBSITES = {
    "Adidas": "https://www.adidas.com",
    "Beyoncé": "https://www.beyonce.com",
    "Bicycling Magazine": "https://www.bicycling.com",
    "BlueCross BlueShield": "https://www.bcbs.com",
    "Columbia University": "https://www.columbia.edu",
    "Condé Nast": "https://www.condenast.com",
    "Dartmouth": "https://home.dartmouth.edu",
    "Enel": "https://www.enel.com",
    "Humana": "https://www.humana.com",
    "Lexia Learning": "https://www.lexialearning.com",
    "Market Basket": "https://www.shopmarketbasket.com",
    "Men's Health": "https://www.menshealth.com",
    "NPR": "https://www.npr.org",
    "Optum": "https://www.optum.com",
    "Penn State": "https://www.psu.edu",
    "Prevention": "https://www.prevention.com",
    "Princeton University": "https://www.princeton.edu",
    "SELF": "https://www.self.com",
    "Special Olympics Massachusetts": "https://www.specialolympicsma.org",
    "United Healthcare": "https://www.uhc.com",
    "Vicinity Energy": "https://www.vicinityenergy.us",
    "Women's Health": "https://www.womenshealthmag.com",
    "Bally Ribbon Mills": "https://www.ballyribbon.com",
    "Citizens Energy": "https://www.citizensenergy.com",
    "Clearasil": "https://www.clearasil.us",
    "Coty": "https://www.coty.com",
    "Eat This, Not That!": "https://www.eatthis.com",
    "Esco Optics": "https://www.escooptics.com",
    "Faith Hill & Tim McGraw": "https://www.faithhill.com",
    "Foxcroft Academy": "https://www.foxcroftacademy.org",
    "Gray Decision Intelligence": "https://www.grayassociates.com",
    "HealthInsurance.com": "https://www.healthinsurance.com",
    "HHAF (Hip Hop Architecture Foundation)": "https://www.hiphoparchitecture.com",
    "Imaginatik": "https://www.imaginatik.com",
    "Judge Baker Children's Center": "https://www.jbcc.harvard.edu",
    "Lightfully Health": "https://www.lightfully.com",
    "Linkwell Health": "https://www.linkwellhealth.com",
    "Mass Biotech Council": "https://www.massbio.org",
    "Middlesex Community College": "https://www.middlesex.mass.edu",
    "Next Avenue": "https://www.nextavenue.org",
    "Northeast Animal Shelter": "https://www.northeastanimalshelter.org",
    "Oldways": "https://www.oldwayspt.org",
    "Organic Gardening": "https://www.organicgardening.com",
    "PopHealth": "https://www.pophealth.com",
    "Rodale Publishing": "https://www.rodale.com",
    "RollWorks": "https://www.rollworks.com",
    "Runner's World": "https://www.runnersworld.com",
    "Safewaze": "https://www.safewaze.com",
    "Sasaki": "https://www.sasaki.com",
    "Slendertone": "https://www.slendertone.com",
    "Sonima": "https://www.sonima.com",
    "SquareWorks": "https://www.squareworks.com",
    "TeachersConnect": "https://www.teachersconnect.com",
    "WorkBar": "https://www.workbar.com",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated = 0
    for name, website in WEBSITES.items():
        cursor.execute(
            "UPDATE companies SET website = ? WHERE name = ? AND status = 'client'",
            (website, name)
        )
        if cursor.rowcount > 0:
            print(f"  Updated: {name} -> {website}")
            updated += 1

    conn.commit()
    conn.close()
    print(f"\nDone! Updated {updated} clients with websites.")

if __name__ == "__main__":
    main()

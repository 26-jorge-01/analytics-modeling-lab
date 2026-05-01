# SECOP Agency Entity Resolution (ER)

This module implements a high-fidelity, geography-aware Master Data Management (MDM) pipeline to resolve duplicated government agencies in the SECOP II dataset.

## 🧠 The "Triple-Lock" Strategy
To prevent false-positive merges between different municipalities (e.g., "Secretaría de Hacienda" in Bogotá vs. Medellín), we use a **Triple-Lock Blocking Key**:
`NIT (Base) + Departamento + Ciudad`

This isolates comparisons into "Geographic Islands," ensuring that the trigonometric similarity engine only compares variants of the same physical entity.

## 🏛️ 4-Tier Waterfall Resolution
Every agency variant is assigned a `linkage_tier` based on the following hierarchy:

1. **TIER 1: SEED OVERRIDE** (Manual logic provided in `agency_overrides.csv`)
2. **TIER 2: IS THE ANCHOR** (The "Golden Record" elected by contract volume and name length)
3. **TIER 3: MATCHED TO ANCHOR** (Automated fuzzy match with `score ≥ 0.60`)
4. **TIER 4: ISOLATED** (Failed match, treated as a unique singleton)

## 🔍 The "Safety Net" Audit Queue
We provide a unified audit view `audit_secop__agency_gray_areas` that flags:
- **Cross-City Matches:** Potential merges that were separated by geography.
- **Cross-NIT Matches:** Potential typos in NIT numbers (different NIT, identical name).
- **Near-Misses:** Scores between 0.40 and 0.60 that might require manual merging.

## 🛠️ Performance & Scale
- **GiST Indexing:** The `int_secop__agencies_base` table uses a Trigram GiST index for fast fuzzy searching.
- **Acronym Expansion:** Integrated registry translates "ICBF" → "Instituto Colombiano..." before matching.
- **Suffix Stripping:** Multi-pass regex removes "S.A.S", "E.S.P.", and other legal boilerplate.

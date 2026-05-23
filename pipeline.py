import os
from typing import Optional
from ingestion.usgs_fetcher import USGSDataFetcher
from ingestion.parcel_loader import ParcelLoader
from spatial.intersection_engine import SpatialIntersectionEngine
from ingestion.offline_recorder import OfflineRecorderImporter
from parser.document_analyzer import DocumentAnalyzer
from scoring.lead_scorer import LeadScorer

class ArbitragePipeline:
    def __init__(self, target_state: str = "TX"):
        self.geology_fetcher = USGSDataFetcher()
        self.parcel_loader = ParcelLoader()
        self.spatial_engine = SpatialIntersectionEngine()
        self.recorder_importer = OfflineRecorderImporter()
        self.document_analyzer = DocumentAnalyzer()
        self.scorer = LeadScorer(target_state=target_state)

    def run_mvp_pipeline(self, geology_filepath: str, parcel_filepath: str, offline_deed_export_path: str):
        print("\n--- Starting MVP Pipeline ---")

        # 1. Ingest Geology
        print("\n[Step 1] Ingesting Geology Data")
        geology_gdf = self.geology_fetcher.load_local_geology(geology_filepath)

        # 2. Ingest Parcels
        print("\n[Step 2] Ingesting Parcel Data")
        parcels_gdf = self.parcel_loader.load_parcels(parcel_filepath)

        # 3. Spatial Intersection (In-memory fallback for MVP without PostGIS running)
        print("\n[Step 3] Running Spatial Intersection")
        intersected_gdf = self.spatial_engine.find_intersections(parcels_gdf, geology_gdf)

        # Deduplicate APNs to prevent multiple leads from overlapping geological features
        if "APN" in intersected_gdf.columns:
            # Sort by a composite spatial proxy score to ensure we keep the highest-value geology polygon
            # for the lead, rather than just the one with the biggest geometric overlap sliver.
            if "overlap_ratio" in intersected_gdf.columns and "probability_score" in intersected_gdf.columns:
                intersected_gdf["_spatial_proxy"] = (
                    intersected_gdf["probability_score"].fillna(0.9) * 0.3 +
                    intersected_gdf["overlap_ratio"].fillna(0.0) * 0.2
                )
                intersected_gdf = intersected_gdf.sort_values("_spatial_proxy", ascending=False)
            elif "overlap_ratio" in intersected_gdf.columns:
                intersected_gdf = intersected_gdf.sort_values("overlap_ratio", ascending=False)

            intersected_gdf = intersected_gdf.drop_duplicates(subset=["APN"], keep="first")

        print(f"Found {len(intersected_gdf)} unique intersecting parcels.")

        if len(intersected_gdf) == 0:
            print("No intersecting parcels found. Exiting pipeline.")
            return []

        # 4. Load Recorder Documents
        print("\n[Step 4] Loading Recorder Documents")
        all_deeds = self.recorder_importer.load_csv_export(offline_deed_export_path)

        # 5 & 6. Classify Severance and Lease Signals, and Score
        print("\n[Step 5 & 6] Classifying Documents & Scoring Leads")
        leads = []

        # Group deeds by APN
        deeds_by_apn = {}
        for deed in all_deeds:
            apn = deed.get("APN")
            if apn:
                if apn not in deeds_by_apn:
                    deeds_by_apn[apn] = []
                deeds_by_apn[apn].append(deed)

        for index, row in intersected_gdf.iterrows():
            apn = row.get("APN", "Unknown")
            owner_state = row.get("OWNER_STATE", "TX")

            # Retrieve real spatial overlap and geology data
            # Requires `overlap_ratio` and `probability_score` computed by intersection engine / fetcher
            overlap_ratio = row.get("overlap_ratio", 1.0)
            geology_confidence = row.get("probability_score", 0.9) # default to 0.9 if absent

            # Look up deeds for this APN
            parcel_deeds_raw = deeds_by_apn.get(apn, [])

            # If we have no recorder history, we cannot assume it is unleased or severed.
            if not parcel_deeds_raw:
                is_severed = False
                is_unleased = False
            else:
                is_severed = False
                parcel_deed_history = []

                # Analyze each deed
                for raw_deed in parcel_deeds_raw:
                    # Use the document text/legal description for heuristic parsing
                    text_to_analyze = raw_deed.get("LegalDescription", "") + " " + raw_deed.get("DocumentType", "")
                    parsed_data = self.document_analyzer.parse_legal_text(text_to_analyze)
                    # Ensure we retain the document type and date
                    parsed_data["DocumentType"] = raw_deed.get("DocumentType", "UNKNOWN")
                    parsed_data["Date"] = raw_deed.get("Date")

                    if parsed_data.get("is_mineral_severed"):
                        is_severed = True

                    parcel_deed_history.append(parsed_data)

                # Audit lease history
                has_active_lease = self.document_analyzer.audit_lease_history(parcel_deed_history)
                is_unleased = not has_active_lease

            # Score
            score_data = self.scorer.generate_lead_score(
                geology_confidence=geology_confidence,
                parcel_overlap_ratio=overlap_ratio,
                is_severed=is_severed,
                is_unleased=is_unleased,
                owner_state=owner_state
            )

            lead = {
                "APN": apn,
                "Score": score_data["total_score"],
                "Is_Severed": is_severed,
                "Is_Unleased": is_unleased,
                "Owner_State": owner_state
            }
            leads.append(lead)

        print("\n--- Pipeline Complete ---")

        # Sort leads by score descending
        leads.sort(key=lambda x: x["Score"], reverse=True)
        return leads

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the SAE MVP Pipeline")
    parser.add_argument("--geology", required=True, help="Path to geology GeoJSON")
    parser.add_argument("--parcels", required=True, help="Path to parcel GeoJSON")
    parser.add_argument("--deeds", required=True, help="Path to offline deeds CSV")
    args = parser.parse_args()

    pipeline = ArbitragePipeline()
    results = pipeline.run_mvp_pipeline(args.geology, args.parcels, args.deeds)

    print("\nTop 5 Leads:")
    for i, lead in enumerate(results[:5]):
        print(f"{i+1}. APN: {lead['APN']} | Score: {lead['Score']} | Severed: {lead['Is_Severed']} | Unleased: {lead['Is_Unleased']}")

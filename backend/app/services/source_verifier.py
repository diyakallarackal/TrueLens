import os
from typing import Dict, List, Any, Optional
from app.services.metadata_verifier import MetadataVerifier
from app.services.c2pa_inspector import inspect_c2pa_provenance
from app.services.external_reverse_search import ExternalReverseSearchVerifier


class TrueLensSourceVerifierSuite:
    """
    Unified Source Verification & Provenance Suite.
    Combines Metadata Verification, C2PA Content Credentials Inspection,
    External Reverse Search Providers, Timeline Generation, and 'WHAT WE FOUND' observations.
    """

    def __init__(self):
        self.metadata_verifier = MetadataVerifier()
        self.reverse_search_verifier = ExternalReverseSearchVerifier()

    def run_verification(
        self,
        file_bytes: bytes,
        metadata: Dict[str, Any],
        media_type: str = "image",
        filename: str = "",
        mime_type: str = "",
    ) -> Dict[str, Any]:
        # 1. Media-Specific Metadata Assessment
        if media_type == "video":
            meta_res = self.metadata_verifier.verify_video_metadata(metadata, filename, len(file_bytes))
        elif media_type == "audio":
            meta_res = self.metadata_verifier.verify_audio_metadata(metadata, filename, len(file_bytes))
        else:
            meta_res = self.metadata_verifier.verify_image_metadata(metadata, filename, len(file_bytes))

        # 2. C2PA / Content Credentials Inspection
        c2pa_res = inspect_c2pa_provenance(file_bytes, mime_type)

        # 3. External Reverse Search Assessment
        reverse_res = self.reverse_search_verifier.verify(file_bytes, metadata, mime_type)

        # 4. Build Provenance Timeline
        has_c2pa = c2pa_res.get("has_c2pa", False)
        c2pa_label = c2pa_res.get("c2pa_status", "No Content Credentials found")

        has_meta = meta_res.get("has_metadata", False)
        software = metadata.get("software_detected") or (meta_res.get("codec") if media_type != "image" else None)

        timeline = [
            {
                "stage": "Content Credentials",
                "status": "detected" if has_c2pa else "not_detected",
                "label": c2pa_label,
                "icon": "c2pa",
            },
            {
                "stage": "Metadata Inspection",
                "status": "detected" if has_meta else "not_available",
                "label": meta_res.get("summary", "Metadata extracted."),
                "icon": "meta",
            },
            {
                "stage": "Editing Indicators",
                "status": "detected" if software and software != "Not available" else "not_detected",
                "label": f"Software tag recorded ({software})" if software and software != "Not available" else "No software/editor tags detected in header",
                "icon": "edit",
            },
            {
                "stage": "External Source Search",
                "status": reverse_res.get("status", "unconfigured"),
                "label": reverse_res.get("message", "External source search is not configured."),
                "icon": "search",
            },
        ]

        # 5. Build 'WHAT WE FOUND' Observation List
        what_we_found = []

        if has_meta:
            what_we_found.append("Metadata was successfully extracted.")
        else:
            what_we_found.append("No embedded metadata header was found.")

        if media_type == "image":
            if metadata.get("has_camera_hardware"):
                make = metadata.get("camera_make") or ""
                model = metadata.get("camera_model") or ""
                what_we_found.append(f"Genuine camera hardware tags detected ({make} {model}).".strip())
            if metadata.get("software_detected"):
                what_we_found.append(f"Editing software information was detected in header ({metadata['software_detected']}).")
        elif media_type == "audio":
            if metadata.get("sample_rate"):
                what_we_found.append(f"Audio stream decoded: {metadata.get('sample_rate')} Hz, {metadata.get('channels')} channel(s).")
        elif media_type == "video":
            if metadata.get("width"):
                what_we_found.append(f"Video container decoded: {metadata.get('width')}x{metadata.get('height')} @ {metadata.get('fps')} FPS.")
            if metadata.get("has_audio"):
                what_we_found.append("Embedded audio track detected and evaluated.")
            else:
                what_we_found.append("No audio track detected in video container.")

        if has_c2pa:
            what_we_found.append(f"C2PA Content Credentials detected: {c2pa_res.get('issuer', 'Signed manifest')}.")
        else:
            what_we_found.append("No Content Credentials were detected.")

        what_we_found.append(reverse_res.get("message", "External source search is not configured."))

        return {
            "timeline": timeline,
            "what_we_found": what_we_found,
            "c2pa": c2pa_res,
            "metadata_assessment": meta_res,
            "external_search": reverse_res,
        }

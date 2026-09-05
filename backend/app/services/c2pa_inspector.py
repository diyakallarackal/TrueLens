import io
from typing import Dict, Any, Optional

try:
    import c2pa
    C2PA_LIB_AVAILABLE = True
except ImportError:
    C2PA_LIB_AVAILABLE = False


def inspect_c2pa_provenance(file_bytes: bytes, mime_type: str = "") -> Dict[str, Any]:
    """
    Inspects image or audio binary for C2PA / Content Credentials metadata.
    Never fabricates provenance or validation status.
    """
    result: Dict[str, Any] = {
        "has_c2pa": False,
        "c2pa_status": "No Content Credentials found",
        "manifest_title": None,
        "issuer": None,
        "signature_valid": None,
        "claim_generator": None,
        "actions": [],
    }

    # First check raw binary signature bytes for JUMBF / C2PA marker box
    has_jumbf_bytes = (b"jumb" in file_bytes[:10000] or b"c2pa" in file_bytes[:10000])

    if C2PA_LIB_AVAILABLE:
        try:
            # Use c2pa Reader if supported format
            reader = c2pa.Reader.from_stream(mime_type or "image/jpeg", io.BytesIO(file_bytes))
            manifest_json = reader.json()
            if manifest_json:
                result["has_c2pa"] = True
                result["c2pa_status"] = "Content Credentials manifest detected"
                active_manifest = manifest_json.get("active_manifest", {})
                result["manifest_title"] = active_manifest.get("title")
                result["claim_generator"] = active_manifest.get("claim_generator")
                
                signature_info = active_manifest.get("signature_info", {})
                result["issuer"] = signature_info.get("issuer")
                result["signature_valid"] = active_manifest.get("validation_status") == "valid"
                
                actions = active_manifest.get("assertions", [])
                result["actions"] = [a.get("label") for a in actions if "label" in a]
                return result
        except Exception:
            # If c2pa parsing raises an exception, fallback to signature marker check
            pass

    if has_jumbf_bytes:
        result["has_c2pa"] = True
        result["c2pa_status"] = "Content Credentials (JUMBF) marker present in media header"

    return result

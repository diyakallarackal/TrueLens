from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.detectors.real_analyzer import RealImageAnalyzer
from app.services.detectors.real_audio_analyzer import RealAudioAnalyzer
from app.services.detectors.real_video_analyzer import RealVideoAnalyzer
from app.database import save_analysis

router = APIRouter()
image_analyzer = RealImageAnalyzer()
audio_analyzer = RealAudioAnalyzer()
video_analyzer = RealVideoAnalyzer()

MAX_IMAGE_SIZE = 25 * 1024 * 1024   # 25MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file (JPEG, PNG, WebP, TIFF, BMP up to 25MB),
    performs real multi-signal image forensics, stores result in DB, and returns evaluation report.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file stream: {str(e)}"
        )

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed threshold of 25MB."
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    try:
        result = await image_analyzer.analyze(contents, file.filename)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during image forensic processing: {str(err)}"
        )

    try:
        save_analysis(result.model_dump())
    except Exception:
        pass

    return result


@router.post("/analyze/audio")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Accepts an uploaded audio file (WAV, MP3, M4A, FLAC up to 50MB),
    performs real acoustic feature extraction, stores result in DB, and returns evaluation report.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file stream: {str(e)}"
        )

    if len(contents) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file size exceeds maximum allowed threshold of 50MB."
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty (0 bytes)."
        )

    try:
        result = await audio_analyzer.analyze(contents, file.filename)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during audio forensic processing: {str(err)}"
        )

    try:
        save_analysis(result.model_dump())
    except Exception:
        pass

    return result


@router.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Accepts an uploaded video file (MP4, MOV, WebM, AVI, MKV up to 100MB),
    samples representative keyframes, evaluates frame MAD optical flow & ELA compression variance,
    extracts & analyzes audio track forensics, stores result in DB, and returns structured evaluation report.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file stream: {str(e)}"
        )

    if len(contents) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Video file size exceeds maximum allowed threshold of 100MB."
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded video file is empty (0 bytes)."
        )

    try:
        result = await video_analyzer.analyze(contents, file.filename)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during video forensic processing: {str(err)}"
        )

    try:
        save_analysis(result.model_dump())
    except Exception:
        pass

    return result

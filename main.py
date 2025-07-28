import asyncio
import logging
import os
import uuid

import cv2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame
from ultralytics import YOLO

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI()

# 정적 파일 마운트
ROOT = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(ROOT, "static")), name="static")

# PeerConnection을 저장하기 위한 집합
pcs = set()

# YOLO 모델 로드
try:
    model = YOLO("yolov8n.pt")
    logger.info("YOLO model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading YOLO model: {e}")
    model = None


class VideoProcessorTrack(MediaStreamTrack):
    """
    프레임에 YOLOv8 객체 탐지를 적용하는 비디오 스트림 트랙입니다.
    """
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()

        if model is None:
            # 모델이 로드되지 않았으면 원본 프레임을 반환
            return frame

        # aiortc의 VideoFrame을 numpy 배열로 변환
        img = frame.to_ndarray(format="bgr24")

        # 객체 탐지 수행
        results = model.predict(img, device="cuda", verbose=False)

        # 결과(바운딩 박스)를 프레임에 그리기
        annotated_frame = results[0].plot()

        # 주석이 달린 numpy 배열로부터 새로운 VideoFrame 생성
        new_frame = VideoFrame.from_ndarray(annotated_frame, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame


@app.get("/")
async def index():
    """index.html 파일을 서빙합니다."""
    html_path = os.path.join(ROOT, "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/offer")
async def offer(request: Request):
    """WebRTC offer를 처리하고 answer를 반환합니다."""
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"
    pcs.add(pc)
    logger.info(f"[{pc_id}] created")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"[{pc_id}] Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            logger.info(f"[{pc_id}] Connection failed, closing.")
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"[{pc_id}] Track {track.kind} received")
        if track.kind == "video":
            local_video = VideoProcessorTrack(track)
            pc.addTrack(local_video)
            logger.info(f"[{pc_id}] Added video processing track")

    # offer 처리
    await pc.setRemoteDescription(offer)

    # answer 생성 및 전송
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    logger.info(f"[{pc_id}] Answer created and sent")
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


@app.on_event("shutdown")
async def on_shutdown():
    """서버 종료 시 모든 PeerConnection을 닫습니다."""
    logger.info("Shutting down, closing all peer connections")
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
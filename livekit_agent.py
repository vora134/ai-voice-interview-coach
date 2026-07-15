# 1. uv run livekit_agent.py dev
# 2. uv run backend.py
# 3. python frontend.py

from __future__ import annotations

import json
import logging
import socket
import sys

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, RunContext, function_tool, room_io
from livekit.plugins import noise_cancellation, silero

from coach import score_answer

load_dotenv()


class InterviewCoachAgent(Agent):
    def __init__(self, candidate: dict | None = None) -> None:
        candidate = candidate or {}
        name = candidate.get("name") or "the candidate"
        role = candidate.get("role") or "software developer"
        experience = candidate.get("experience") or "fresher"
        skills = candidate.get("skills") or "Python and AI"
        mode = candidate.get("mode") or "mixed"
        resume = candidate.get("resume") or "No resume summary provided."

        super().__init__(
            instructions=(
                "You are an expert technical interviewer conducting a realistic voice interview. "
                f"The candidate is {name}, interviewing for {role}. "
                f"Experience level: {experience}. Interview mode: {mode}. "
                f"Key candidate skills: {skills}. Resume/background summary: {resume}. "
                "Structure the interview into 3 phases: "
                "1. Brief greeting and asking the candidate to introduce themselves. "
                "2. Technical deep dive: Ask 2-3 specific technical questions challenging their declared stack (e.g., neural networks in DL, FastAPI router structures, LangGraph state management, RAG semantic search, or MCP server integration). "
                "3. Behavioral scenario: Ask a situational engineering question. "
                "After the candidate answers a core question, call the analyze_interview_answer tool, wait for the score, and reply with: "
                "a) Their numerical score, b) One positive aspect of their response, c) One technical improvement or correction, and d) Ask the next question. "
                "If the candidate doesn't know, teach them a simple, high-quality answer, then proceed to the next question. "
                "Keep your voice tone professional, encouraging, yet technically rigorous. "
                "Use plain ASCII punctuation only. Keep your questions and responses concise."
            )
        )

    
    @function_tool
    async def analyze_interview_answer(
        self,
        context: RunContext,
        question: str,
        transcript: str,
    ) -> dict:
        """
        Score a spoken interview answer and return coaching feedback.

        Args:
            question: The interview question that was asked.
            transcript: The user's answer transcript.
        """
        del context
        return score_answer(question, transcript)


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    candidate = {}
    try:
        participant = await ctx.wait_for_participant()
        candidate = json.loads(participant.metadata or "{}")
    except Exception:
        logging.exception("Could not read participant metadata")

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4o-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
        allow_interruptions=True,
        min_endpointing_delay=1.2,
        min_interruption_words=3,
    )

    await session.start(
        agent=InterviewCoachAgent(candidate),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
            text_output=room_io.TextOutputOptions(sync_transcription=True),
        ),
    )

    await session.generate_reply(
        instructions=(
            "Greet the candidate by name if available, then ask the first interview "
            "question based on their role, skills, or resume."
        )
    )


_lock_socket = None

def ensure_singleton(port: int):
    global _lock_socket
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.bind(('127.0.0.1', port))
    except OSError:
        print(f"\n❌ ERROR: Another instance of this script is already running (locked port {port})!")
        print("Please close any other terminal windows or background python processes.")
        sys.exit(1)


if __name__ == "__main__":
    ensure_singleton(55055)
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(server)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socket
import sys

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Voice Interview Coach - Room Session</title>
    <script src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
      :root {
        --bg-slate: #0b0f19;
        --panel-dark: #111827;
        --panel-darker: #0d111c;
        --ink-light: #f3f4f6;
        --ink-muted: #9ca3af;
        --border-gray: #1f2937;
        --accent-cyan: #38bdf8;
        --accent-blue: #2563eb;
        --accent-hover: #1d4ed8;
        --soft-bg: rgba(56, 189, 248, 0.05);
        --green-success: #10b981;
        --red-danger: #ef4444;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-slate);
        color: var(--ink-light);
        display: flex;
        flex-direction: column;
      }

      main {
        width: min(1280px, calc(100% - 32px));
        margin: 24px auto;
        display: grid;
        grid-template-columns: 400px 1fr;
        gap: 24px;
        flex: 1;
      }

      section {
        background: var(--panel-dark);
        border: 1px solid var(--border-gray);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
      }

      .profile {
        padding: 24px;
      }

      .eyebrow {
        margin: 0 0 6px;
        color: var(--accent-cyan);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'Outfit', sans-serif;
      }

      h1 {
        margin: 0;
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.2;
        background: linear-gradient(135deg, #38bdf8, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }

      h2 {
        margin: 0;
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 600;
      }

      .intro {
        color: var(--ink-muted);
        font-size: 0.95rem;
        line-height: 1.55;
        margin: 10px 0 20px;
      }

      .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }

      label {
        display: block;
        margin-bottom: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--ink-light);
      }

      input,
      select,
      textarea {
        width: 100%;
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        padding: 10px 12px;
        color: var(--ink-light);
        font: inherit;
        font-size: 0.9rem;
        background: var(--panel-darker);
        transition: border-color 0.2s;
      }

      input:focus,
      select:focus,
      textarea:focus {
        outline: none;
        border-color: var(--accent-cyan);
      }

      textarea {
        min-height: 100px;
        resize: vertical;
        line-height: 1.45;
      }

      .field {
        margin-top: 12px;
      }

      .buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 20px;
      }

      button {
        min-height: 42px;
        border: 0;
        border-radius: 8px;
        padding: 0 16px;
        color: #fff;
        background: var(--accent-blue);
        font: inherit;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s, opacity 0.2s;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }

      button:hover {
        background: var(--accent-hover);
      }

      button.secondary {
        background: #1f2937;
        color: var(--ink-light);
        border: 1px solid var(--border-gray);
      }

      button.secondary:hover {
        background: #374151;
      }

      button.danger {
        background: var(--red-danger);
      }

      button.danger:hover {
        background: #dc2626;
      }

      button:disabled {
        cursor: not-allowed;
        opacity: 0.4;
      }

      .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 16px;
        padding: 8px 14px;
        border: 1px solid var(--border-gray);
        border-radius: 999px;
        color: var(--ink-muted);
        background: var(--panel-darker);
        font-size: 0.85rem;
      }

      .dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #4b5563;
      }

      .dot.connected {
        background: var(--green-success);
        box-shadow: 0 0 8px var(--green-success);
        animation: pulse 1.5s infinite;
      }

      @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
      }

      .stage {
        display: grid;
        grid-template-rows: auto 1fr auto;
        min-height: calc(100vh - 48px);
        overflow: hidden;
      }

      .stage-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        padding: 16px 24px;
        border-bottom: 1px solid var(--border-gray);
        background: var(--panel-darker);
      }

      .room-pill {
        padding: 6px 12px;
        border-radius: 999px;
        background: var(--soft-bg);
        border: 1px solid rgba(56, 189, 248, 0.2);
        color: var(--accent-cyan);
        font-weight: 700;
        font-size: 0.8rem;
        white-space: nowrap;
      }

      .conversation {
        min-height: 420px;
        overflow-y: auto;
        padding: 24px;
        background: radial-gradient(circle at bottom right, rgba(37, 99, 235, 0.04), transparent 60%);
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .empty {
        display: grid;
        place-items: center;
        min-height: 360px;
        color: var(--ink-muted);
        text-align: center;
        line-height: 1.6;
        border: 1px dashed var(--border-gray);
        border-radius: 8px;
        padding: 24px;
      }

      .message {
        max-width: 76%;
        padding: 12px 16px;
        border-radius: 12px;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        font-size: 0.95rem;
        animation: slideIn 0.2s ease-out;
      }

      @keyframes slideIn {
        from { transform: translateY(8px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }

      .message small {
        display: block;
        margin-bottom: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .message.user {
        margin-left: auto;
        background: var(--accent-blue);
        color: #fff;
        border-bottom-right-radius: 2px;
      }

      .message.user small {
        color: rgba(255, 255, 255, 0.7);
      }

      .message.agent {
        margin-right: auto;
        background: var(--panel-darker);
        border: 1px solid var(--border-gray);
        color: var(--ink-light);
        border-bottom-left-radius: 2px;
      }

      .message.agent small {
        color: var(--accent-cyan);
      }

      .message.system {
        max-width: 100%;
        margin: 4px auto;
        background: transparent;
        color: var(--ink-muted);
        border: 0;
        box-shadow: none;
        font-style: italic;
        font-size: 0.85rem;
        text-align: center;
      }

      .stage-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        padding: 16px 24px;
        border-top: 1px solid var(--border-gray);
        background: var(--panel-darker);
      }

      .hint {
        color: var(--ink-muted);
        font-size: 0.85rem;
        line-height: 1.4;
      }

      .mini-report {
        margin-top: 16px;
        padding: 12px 14px;
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        background: var(--panel-darker);
        color: var(--ink-muted);
        font-size: 0.85rem;
        line-height: 1.5;
      }

      /* Report Box Styling inside conversation */
      .report-box {
        background: var(--panel-darker);
        border: 1px solid var(--border-gray);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.4s ease;
      }

      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      .report-box h2 {
        margin-top: 0;
        margin-bottom: 16px;
        font-family: 'Outfit', sans-serif;
        font-size: 20px;
        border-bottom: 1px solid var(--border-gray);
        padding-bottom: 10px;
        color: var(--accent-cyan);
      }

      .report-grid {
        display: grid;
        grid-template-columns: 200px 1fr;
        gap: 20px;
        margin-bottom: 20px;
      }

      .score-card {
        background: var(--panel-dark);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
      }

      .score-ring {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 10px;
      }

      .score-strong { border: 6px solid var(--green-success); color: var(--green-success); }
      .score-decent { border: 6px solid #d4a373; color: #d4a373; }
      .score-poor { border: 6px solid var(--red-danger); color: var(--red-danger); }

      .score-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 2px;
      }

      .score-sub {
        font-size: 0.75rem;
        color: var(--ink-muted);
        text-transform: uppercase;
      }

      .metrics-card {
        background: var(--panel-dark);
        border: 1px solid var(--border-gray);
        border-radius: 10px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }

      .metric-row {
        display: flex;
        justify-content: space-around;
        gap: 10px;
        text-align: center;
      }

      .metric-item {
        flex: 1;
      }

      .metric-val {
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--ink-light);
      }

      .metric-lbl {
        font-size: 0.75rem;
        color: var(--ink-muted);
        text-transform: uppercase;
      }

      .star-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 10px;
      }

      .star-chip {
        padding: 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        text-align: center;
        font-weight: 600;
      }

      .star-chip.met {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: var(--green-success);
      }

      .star-chip.missing {
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.15);
        color: var(--ink-muted);
      }

      .tips-box {
        background: rgba(56, 189, 248, 0.04);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        padding: 16px;
        margin-top: 15px;
      }

      .tips-box h4 {
        margin: 0 0 8px 0;
        color: var(--accent-cyan);
      }

      .tips-box ul {
        margin: 0;
        padding-left: 20px;
        font-size: 0.9rem;
        line-height: 1.5;
        color: var(--ink-light);
      }

      .tips-box li {
        margin-bottom: 6px;
      }

      .mic-help {
        margin-top: 12px;
        padding: 8px 12px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        font-size: 0.8rem;
        line-height: 1.4;
        color: #ff7b72;
      }



      @media (max-width: 960px) {
        main {
          grid-template-columns: 1fr;
        }
        .stage {
          min-height: 500px;
        }
      }
    </style>
  </head>
  <body>
    <div id="micErrorModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; align-items: center; justify-content: center; padding: 20px;">
      <div style="background: #161b22; border: 1px solid #da3633; border-radius: 12px; max-width: 550px; width: 100%; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <h3 style="margin-top: 0; color: #ff7b72; font-family: 'Outfit', sans-serif; display: flex; align-items: center; gap: 8px;">
          ⚠️ Microphone Access Blocked
        </h3>
        <p style="color: #c9d1d9; font-size: 0.95rem; line-height: 1.5; margin-bottom: 16px;">
          The browser reported: <strong>"Permission denied by system"</strong>. This means Chrome/Edge is blocked from accessing your microphone either by the browser settings or by Windows privacy controls.
        </p>
        
        <h4 style="margin: 12px 0 6px 0; color: #58a6ff; font-size: 0.9rem; text-transform: uppercase;">Step 1: Check Browser Permissions</h4>
        <p style="color: #8b949e; font-size: 0.85rem; line-height: 1.4; margin: 0 0 12px 0;">
          Click the <strong>Lock icon 🔒</strong> at the left of the URL bar (next to <code style="background: #0d1117; padding: 2px 6px; border-radius: 4px;">localhost:3000</code>) and verify that <strong>Microphone</strong> is set to <strong>Allow</strong>.
        </p>
        
        <h4 style="margin: 12px 0 6px 0; color: #58a6ff; font-size: 0.9rem; text-transform: uppercase;">Step 2: Enable Windows System Access (Most Common)</h4>
        <p style="color: #8b949e; font-size: 0.85rem; line-height: 1.4; margin: 0 0 12px 0;">
          1. Open Windows Settings (Press <strong>Win + I</strong>).<br>
          2. Navigate to <strong>Privacy & Security</strong> &gt; <strong>Microphone</strong>.<br>
          3. Verify that <strong>Microphone access</strong> is toggled <strong>ON</strong>.<br>
          4. Scroll down to <strong>"Let desktop apps access your microphone"</strong> and ensure it is toggled <strong>ON</strong> (so Chrome/Edge can record).
        </p>
        
        <div style="display: flex; justify-content: flex-end; margin-top: 20px; gap: 10px;">
          <button onclick="document.getElementById('micErrorModal').style.display='none'" class="secondary" style="min-height: 36px; padding: 0 12px; background: #1f2937; color: white; border: 1px solid #30363d; border-radius: 8px;">Close</button>
          <button onclick="window.location.reload()" style="min-height: 36px; padding: 0 16px; background: #238636; color: white; border: 0; border-radius: 8px; cursor: pointer; font-weight: bold;">🔄 Reload Page</button>
        </div>
      </div>
    </div>
    <main>
      <section class="profile">
        <p class="eyebrow">LiveKit AI interview room</p>
        <h1>Voice Coach</h1>
        <p class="intro">
          Enter candidate details, connect to your LiveKit agent, and practice a
          personalized interview.
        </p>

        <div class="grid" style="margin-top: 15px;">
          <div>
            <label for="name">Name</label>
            <input id="name" value="Candidate" />
          </div>
          <div>
            <label for="role">Target role</label>
            <input id="role" value="Software Developer" />
          </div>
          <div>
            <label for="experience">Experience</label>
            <input id="experience" value="Fresher" />
          </div>
          <div>
            <label for="mode">Mode</label>
            <select id="mode">
              <option value="mixed">Mixed</option>
              <option value="technical">Technical</option>
              <option value="behavioral">Behavioral</option>
              <option value="project">Project based</option>
              <option value="hr">HR</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label for="skills">Skills</label>
          <input id="skills" value="Python, LiveKit, OpenAI" />
        </div>

        <div class="field">
          <label for="resume">Resume summary</label>
          <textarea id="resume">Built code projects using Python. Interested in voice AI.</textarea>
        </div>

        <div class="field">
          <label for="resumeFile">Upload resume text</label>
          <input id="resumeFile" type="file" accept=".txt,.md,.csv" />
        </div>

        <div class="field">
          <label for="room">Room</label>
          <input id="room" value="interview-demo" />
        </div>

        <div class="buttons" style="margin-top: 20px; border-top: 1px solid var(--border-gray); padding-top: 15px;">
          <button id="connectBtn">🚀 Start</button>
          <button id="muteBtn" class="secondary" disabled>🎙️ Mute</button>
          <button id="disconnectBtn" class="danger" disabled>⏹️ End</button>
        </div>

        <div class="status">
          <span id="dot" class="dot"></span>
          <span id="statusText">Not connected</span>
        </div>

        <div class="mic-help">
          💡 <strong>Microphone Tip:</strong> If connection fails, ensure your browser address bar has microphone permissions allowed.
        </div>
      </section>

      <section class="stage">
        <div class="stage-header">
          <div>
            <p class="eyebrow">Conversation</p>
            <h2>Live Transcript</h2>
          </div>
          <span id="roomPill" class="room-pill">interview-demo</span>
        </div>

        <div id="conversation" class="conversation">
          <div class="empty">
            Configure the profile settings, click <strong>Start</strong> and speak naturally to talk to the AI Coach.
          </div>
        </div>

        <div class="stage-footer">
          <span class="hint">Try: "Tell me about a challenging project you built."</span>
        </div>
      </section>
    </main>

    <script>
      const { Room, RoomEvent, Track } = LivekitClient;

      const els = {
        connect: document.querySelector("#connectBtn"),
        disconnect: document.querySelector("#disconnectBtn"),
        mute: document.querySelector("#muteBtn"),
        status: document.querySelector("#statusText"),
        dot: document.querySelector("#dot"),
        conversation: document.querySelector("#conversation"),
        roomPill: document.querySelector("#roomPill"),
        name: document.querySelector("#name"),
        role: document.querySelector("#role"),
        experience: document.querySelector("#experience"),
        mode: document.querySelector("#mode"),
        roomName: document.querySelector("#room"),
        skills: document.querySelector("#skills"),
        resume: document.querySelector("#resume"),
        resumeFile: document.querySelector("#resumeFile"),
      };

      let room = null;
      let micEnabled = true;
      const transcriptNodes = new Map();

      function value(id) {
        return els[id].value.trim();
      }

      function setStatus(text, connected = false) {
        els.status.textContent = text;
        els.dot.classList.toggle("connected", connected);
      }

      function normalizeText(text) {
        return text
          .replaceAll("â€™", "'")
          .replaceAll("â€œ", '"')
          .replaceAll("â€ ", '"')
          .replaceAll("Â·", "-")
          .replaceAll(/[“”]/g, '"')
          .replaceAll(/[‘’]/g, "'");
      }

      function addMessage(kind, speaker, text, key = "") {
        text = normalizeText(text);
        const finalKey = key || `${kind}-${speaker}-${text.slice(0, 30)}-${Date.now()}`;
        let node = transcriptNodes.get(finalKey);

        if (!node) {
          if (els.conversation.querySelector(".empty")) {
            els.conversation.innerHTML = "";
          }
          node = document.createElement("div");
          node.className = `message ${kind}`;
          node.innerHTML = `<small></small><span></span>`;
          transcriptNodes.set(finalKey, node);
          els.conversation.appendChild(node);
        }

        node.querySelector("small").textContent = speaker;
        node.querySelector("span").textContent = text;
        els.conversation.scrollTop = els.conversation.scrollHeight;
      }

      function participantKind(participant) {
        if (!participant) return "system";
        if (participant.isLocal) return "user";
        return "agent";
      }

      function participantName(participant) {
        if (!participant) return "System";
        if (participant.isLocal) return value("name") || "You";
        return "Interview Coach";
      }

      function handleTranscription(transcription, participant) {
        const segments = transcription.segments || [];
        for (const segment of segments) {
          const text = (segment.text || "").trim();
          if (!text) continue;
          const id = segment.id || `${participant?.identity || "unknown"}-${text}`;
          addMessage(
            participantKind(participant),
            participantName(participant),
            text,
            id
          );
        }
      }

      async function connect() {
        if (room) {
          try {
            room.disconnect();
          } catch (e) {}
        }
        const roomName = value("roomName") || "interview-demo";
        const identity = `${value("name") || "candidate"}-${Date.now()}`;
        const params = new URLSearchParams({
          room: roomName,
          identity,
          name: value("name") || "Candidate",
          role: value("role") || "Software Developer",
          experience: value("experience") || "Fresher",
          mode: value("mode") || "mixed",
          skills: value("skills"),
          resume: value("resume"),
        });

        els.roomPill.textContent = roomName;
        setStatus("Creating secure token...");

        const tokenRes = await fetch(`http://localhost:8787/token?${params}`);
        const data = await tokenRes.json();
        if (!tokenRes.ok || data.error) {
          throw new Error(data.error || "Token request failed");
        }

        room = new Room();

        room.on(RoomEvent.TrackSubscribed, (track) => {
          if (track.kind === Track.Kind.Audio) {
            document.body.appendChild(track.attach());
            addMessage("system", "System", "Agent audio connected.");
          }
        });

        room.on(RoomEvent.ParticipantConnected, (participant) => {
          addMessage("system", "System", `${participant.identity} joined.`);
        });

        room.on(RoomEvent.ParticipantDisconnected, (participant) => {
          addMessage("system", "System", `${participant.identity} left.`);
        });

        if (RoomEvent.TranscriptionReceived) {
          room.on(RoomEvent.TranscriptionReceived, handleTranscription);
        }

        room.on(RoomEvent.Disconnected, () => {
          setStatus("Disconnected");
          els.connect.disabled = false;
          els.disconnect.disabled = true;
          els.mute.disabled = true;
        });

        await room.connect(data.url, data.token);
        await room.localParticipant.setMicrophoneEnabled(true);

        transcriptNodes.clear();
        setStatus(`Connected`, true);
        addMessage("system", "System", "Connected. Speak to begin your interview.");
        els.connect.disabled = true;
        els.disconnect.disabled = false;
        els.mute.disabled = false;
      }

      async function toggleMute() {
        if (!room) return;
        micEnabled = !micEnabled;
        await room.localParticipant.setMicrophoneEnabled(micEnabled);
        els.mute.textContent = micEnabled ? "🎙️ Mute" : "🎙️ Unmute";
      }

      function disconnect() {
        if (room) room.disconnect();
      }



      els.resumeFile.addEventListener("change", async () => {
        const file = els.resumeFile.files[0];
        if (!file) return;
        
        if (file.name.toLowerCase().endsWith(".pdf")) {
          setStatus("Parsing PDF resume...");
          try {
            const formData = new FormData();
            formData.append("file", file);
            
            const res = await fetch("http://localhost:8787/parse-resume", {
              method: "POST",
              body: formData
            });
            const data = await res.json();
            if (res.ok && data.text) {
              els.resume.value = data.text;
              setStatus("PDF parsed successfully");
            } else {
              setStatus("PDF parse failed");
              alert("Failed to parse PDF resume: " + (data.detail || "Unknown error"));
            }
          } catch (e) {
            setStatus("PDF parse error");
            alert("Error parsing PDF resume: " + e.message);
          }
        } else {
          try {
            els.resume.value = (await file.text()).slice(0, 1200);
          } catch(e) {
            alert("Failed to read text file: " + e.message);
          }
        }
      });

      els.connect.addEventListener("click", () => {
        els.connect.disabled = true;
        connect().catch((error) => {
          els.connect.disabled = false;
          setStatus("Connection failed");
          addMessage("system", "Error", error.message);
          const errMsg = (error.message || "").toLowerCase();
          if (errMsg.includes("permission") || errMsg.includes("denied") || error.name === "NotAllowedError") {
            const modal = document.getElementById("micErrorModal");
            if (modal) modal.style.display = "flex";
          }
        });
      });
      els.mute.addEventListener("click", toggleMute);
      els.disconnect.addEventListener("click", disconnect);
     </script>
  </body>
</html>
"""


class FrontendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


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
    ensure_singleton(55057)
    server = ThreadingHTTPServer(("localhost", 3000), FrontendHandler)
    print("Frontend running at http://localhost:3000")
    server.serve_forever()

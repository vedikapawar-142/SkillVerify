/**
 * AI Skill Verification Platform — Real-time MediaPipe & Integrity Proctoring Engine
 * Implements camera face detection (MediaPipe Face Detection) + tab-switch detection.
 * Aligned with Diploma Synopsis Section 7.3 & Table 4:
 *   - Tab / window switch: -5
 *   - Face absent for > 3 seconds: -5
 *   - Multiple faces detected: -10
 *   - Camera interruption: -5
 * Integrity score starts at 100 and is reduced per logged event (min 0).
 */

class IntegrityProctor {
  constructor(options = {}) {
    this.attemptId = options.attemptId || 0;
    this.videoElement = options.videoElement || document.getElementById("proctorVideo");
    this.canvasElement = options.canvasElement || document.getElementById("proctorCanvas");
    this.badgeElement = options.badgeElement || document.getElementById("proctorBadge");
    this.scoreElement = options.scoreElement || document.getElementById("integrityScoreDisplay");
    this.hiddenScoreInput = options.hiddenScoreInput || document.getElementById("integrityScoreInput");
    this.eventsLogElement = options.eventsLogElement || document.getElementById("proctorEventsLog");

    this.integrityScore = 100.0;
    this.stream = null;
    this.cameraUtils = null;
    this.faceDetection = null;
    this.absentConsecutiveTicks = 0;
    this.lastViolationTime = {};
    this.cooldownSeconds = 5; // prevent spamming violations within 5 seconds
    this.isMonitoring = false;

    this.init();
  }

  async init() {
    console.log("[Proctor] Initializing MediaPipe Face Detection & Tab Proctoring...");
    this.setupTabMonitoring();
    await this.setupCamera();
    this.initMediaPipe();
  }

  updateIntegrityScoreUI() {
    if (this.scoreElement) {
      this.scoreElement.textContent = Math.max(0, Math.round(this.integrityScore));
      if (this.integrityScore < 70) {
        this.scoreElement.className = "text-danger fw-bold";
      } else if (this.integrityScore < 85) {
        this.scoreElement.className = "text-warning fw-bold";
      } else {
        this.scoreElement.className = "text-success fw-bold";
      }
    }
    if (this.hiddenScoreInput) {
      this.hiddenScoreInput.value = Math.max(0, Math.round(this.integrityScore));
    }
  }

  logEvent(type, message, deduction) {
    const timestamp = new Date().toLocaleTimeString();
    console.warn(`[Proctor Warning] ${type}: ${message} (-${deduction} pts)`);

    if (this.eventsLogElement) {
      const item = document.createElement("div");
      item.className = "small text-danger mb-1 border-bottom pb-1";
      item.innerHTML = `<span class="badge bg-danger me-1">-${deduction}</span> <span class="text-muted">${timestamp}</span> ${message}`;
      this.eventsLogElement.prepend(item);
    }

    // Send asynchronous beacon/fetch to server
    if (this.attemptId) {
      fetch(`/api/assessment/${this.attemptId}/violation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: type,
          details: message,
          deduction: deduction
        })
      }).catch(err => console.error("[Proctor] Error reporting violation:", err));
    }
  }

  recordViolation(type, message, deduction) {
    const now = Date.now();
    const lastTime = this.lastViolationTime[type] || 0;
    if (now - lastTime < this.cooldownSeconds * 1000) {
      return; // Cooldown active
    }
    this.lastViolationTime[type] = now;
    this.integrityScore = Math.max(0, this.integrityScore - deduction);
    this.updateIntegrityScoreUI();
    this.logEvent(type, message, deduction);

    // Show temporary alert toast or banner
    this.showWarningToast(message);
  }

  showWarningToast(msg) {
    const toast = document.getElementById("proctorAlertToast");
    const toastMsg = document.getElementById("proctorAlertMsg");
    if (toast && toastMsg) {
      toastMsg.textContent = msg;
      toast.classList.remove("d-none");
      setTimeout(() => toast.classList.add("d-none"), 4000);
    }
  }

  setupTabMonitoring() {
    // Visibility API for tab switching
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.recordViolation("tab_switch", "Tab switched or minimized during assessment", 5);
        if (this.badgeElement) {
          this.badgeElement.className = "badge bg-danger";
          this.badgeElement.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> Tab Left`;
        }
      }
    });

    // Window blur event
    window.addEventListener("blur", () => {
      this.recordViolation("tab_switch", "Window lost focus / application switch detected", 5);
    });
  }

  async setupCamera() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("getUserMedia not supported in this browser");
      }
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: "user" },
        audio: false
      });

      if (this.videoElement) {
        this.videoElement.srcObject = this.stream;
        await this.videoElement.play();
      }

      this.isMonitoring = true;
      if (this.badgeElement) {
        this.badgeElement.className = "badge bg-success";
        this.badgeElement.innerHTML = `<i class="bi bi-camera-video-fill"></i> Camera Active`;
      }

      // Track interruption
      const track = this.stream.getVideoTracks()[0];
      track.onended = () => {
        this.recordViolation("camera_interruption", "Webcam hardware disconnected or stopped", 5);
        if (this.badgeElement) {
          this.badgeElement.className = "badge bg-danger";
          this.badgeElement.innerHTML = `<i class="bi bi-camera-video-off-fill"></i> Camera Lost`;
        }
      };

    } catch (err) {
      console.warn("[Proctor] Camera access error:", err);
      this.recordViolation("camera_interruption", "Camera permission denied or camera unavailable", 5);
      if (this.badgeElement) {
        this.badgeElement.className = "badge bg-warning text-dark";
        this.badgeElement.innerHTML = `<i class="bi bi-shield-slash-fill"></i> No Camera Access`;
      }
    }
  }

  initMediaPipe() {
    if (!window.FaceDetection) {
      console.log("[Proctor] MediaPipe script not loaded; running in fallback mode.");
      return;
    }

    try {
      this.faceDetection = new window.FaceDetection({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`
      });

      this.faceDetection.setOptions({
        model: "short",
        minDetectionConfidence: 0.5
      });

      this.faceDetection.onResults((results) => this.onFaceResults(results));

      // Continuously feed frames from videoElement to MediaPipe
      if (this.videoElement && window.Camera) {
        this.cameraUtils = new window.Camera(this.videoElement, {
          onFrame: async () => {
            if (this.videoElement.readyState === 4) {
              await this.faceDetection.send({ image: this.videoElement });
            }
          },
          width: 320,
          height: 240
        });
        this.cameraUtils.start();
      } else if (this.videoElement) {
        // Fallback interval processing
        setInterval(async () => {
          if (this.videoElement && this.videoElement.readyState === 4 && this.faceDetection) {
            try {
              await this.faceDetection.send({ image: this.videoElement });
            } catch (e) {}
          }
        }, 800);
      }
    } catch (e) {
      console.error("[Proctor] Failed to initialize MediaPipe Face Detection:", e);
    }
  }

  onFaceResults(results) {
    if (!this.canvasElement) return;
    const ctx = this.canvasElement.getContext("2d");
    ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

    const faceCount = (results.detections || []).length;

    if (faceCount === 0) {
      this.absentConsecutiveTicks++;
      // If absent for 4 ticks (~3.2 seconds)
      if (this.absentConsecutiveTicks >= 4) {
        this.recordViolation("face_absent", "Face absent from camera frame for > 3 seconds", 5);
        if (this.badgeElement) {
          this.badgeElement.className = "badge bg-danger";
          this.badgeElement.innerHTML = `<i class="bi bi-person-x-fill"></i> Face Absent`;
        }
      }
    } else if (faceCount > 1) {
      this.absentConsecutiveTicks = 0;
      this.recordViolation("multiple_faces", `Multiple faces (${faceCount}) detected in test view`, 10);
      if (this.badgeElement) {
        this.badgeElement.className = "badge bg-danger";
        this.badgeElement.innerHTML = `<i class="bi bi-people-fill"></i> Multiple Faces`;
      }
    } else {
      // Exactly 1 face: All clear
      this.absentConsecutiveTicks = 0;
      if (this.badgeElement) {
        this.badgeElement.className = "badge bg-success";
        this.badgeElement.innerHTML = `<i class="bi bi-shield-check"></i> Monitored & Verified`;
      }
    }
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(t => t.stop());
    }
    if (this.cameraUtils) {
      try { this.cameraUtils.stop(); } catch(e) {}
    }
    this.isMonitoring = false;
  }
}

// Global initialization helper
window.startIntegrityProctor = function(attemptId) {
  window.currentProctor = new IntegrityProctor({ attemptId: attemptId });
};

// Thu âm từ micro (MediaRecorder) kèm đo mức âm lượng theo thời gian thực.
export class Recorder {
  constructor({ onLevel } = {}) {
    this.onLevel = onLevel;
    this.rec = null;
    this.stream = null;
    this.chunks = [];
    this.raf = 0;
  }

  get recording() { return !!this.rec && this.rec.state === "recording"; }

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1 },
    });
    const ctx = new AudioContext();
    const src = ctx.createMediaStreamSource(this.stream);
    const an = ctx.createAnalyser();
    an.fftSize = 1024;
    src.connect(an);
    const data = new Float32Array(an.fftSize);
    const tick = () => {
      an.getFloatTimeDomainData(data);
      let peak = 0;
      for (const v of data) peak = Math.max(peak, Math.abs(v));
      this.onLevel?.(peak);
      this.raf = requestAnimationFrame(tick);
    };
    tick();
    this.ctx = ctx;
    const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "";
    this.rec = new MediaRecorder(this.stream, mime ? { mimeType: mime, audioBitsPerSecond: 256000 } : undefined);
    this.chunks = [];
    this.rec.ondataavailable = (e) => e.data.size && this.chunks.push(e.data);
    this.rec.start();
  }

  stop() {
    return new Promise((resolve) => {
      if (!this.rec) return resolve(null);
      this.rec.onstop = () => {
        cancelAnimationFrame(this.raf);
        this.stream.getTracks().forEach((t) => t.stop());
        this.ctx?.close();
        this.onLevel?.(0);
        const blob = new Blob(this.chunks, { type: this.rec.mimeType || "audio/webm" });
        this.rec = null;
        resolve(blob);
      };
      this.rec.stop();
    });
  }
}

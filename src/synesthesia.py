"""
🦁 Synesthesia — Fusión cross-modal audio → visual.

Convierte audio grabado (micrófono o archivo) en representaciones visuales
ASCII. Inspirado en la sinestesia real: "ver sonidos, oír colores".

Pipeline:
  1. Captura/lectura de audio
  2. Análisis de características (volumen, tono, tempo, frecuencia)
  3. Transcripción (si hay voz)
  4. Generación de visualización ASCII sincronizada

Dependencias opcionales:
  - pyaudio: grabación desde micrófono (pip install pyaudio)
  - faster-whisper: transcripción local (pip install faster-whisper)
  Sin ellas, funciona en modo análisis básico de waveform.
"""
import io
import json
import math
import wave
import struct
import logging
import subprocess
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("synesthesia")


@dataclass
class AudioFeatures:
    """Características extraídas del audio."""
    duration: float = 0.0  # segundos
    sample_rate: int = 0
    n_channels: int = 0
    
    # Volumen/energía
    rms_energy: float = 0.0  # Root Mean Square energy
    peak_amplitude: float = 0.0
    silence_ratio: float = 0.0  # fracción de silencio
    
    # Frecuencia/Tono
    dominant_frequency: float = 0.0  # Hz
    spectral_centroid: float = 0.0
    pitch_estimate: float = 0.0  # Hz estimado
    
    # Tempo/Ritmo
    tempo_bpm: float = 0.0
    beats: list = field(default_factory=list)  # posiciones de beats en segundos
    
    # Fragmentos
    fragments: list = field(default_factory=list)  # análisis por fragmento
    
    # Texto (si hay voz)
    transcription: str = ""


@dataclass
class SynesthesiaConfig:
    """Configuración del procesador Synesthesia."""
    fps: int = 10  # "frames por segundo" para visualización
    ascii_width: int = 80
    ascii_height: int = 20
    fragment_size_ms: int = 100  # tamaño de fragmento para análisis
    enable_transcription: bool = False  # requiere faster-whisper


class SynesthesiaProcessor:
    """
    Procesa audio y genera visualizaciones ASCII.
    Sinestesia artificial: convierte sonido en patrones visuales.
    """

    def __init__(self, config: Optional[SynesthesiaConfig] = None):
        self.config = config or SynesthesiaConfig()

    # ─── Carga de audio ───────────────────────────────────────

    def load_audio(self, source) -> Optional[np.ndarray]:
        """
        Carga audio desde archivo, bytes o grabación.
        
        Args:
            source: Ruta a .wav, bytes WAV, o None para grabar desde mic
        
        Returns:
            numpy array con audio mono, o None si error
        """
        try:
            if source is None:
                return self._record_microphone()
            if isinstance(source, str):
                return self._load_from_file(source)
            if isinstance(source, bytes):
                return self._load_from_bytes(source)
            if isinstance(source, np.ndarray):
                return source
        except Exception as e:
            logger.error(f"Error cargando audio: {e}")
            return None
        return None

    def _load_from_file(self, path: str) -> Optional[np.ndarray]:
        """Carga audio desde archivo."""
        # Intentar con scipy.io.wavfile primero
        try:
            from scipy.io import wavfile
            rate, data = wavfile.read(path)
            if data.ndim > 1:
                data = data.mean(axis=1)  # mono
            return data.astype(float)
        except ImportError:
            pass

        # Fallback: leer con wave estándar
        try:
            with wave.open(path, 'rb') as wf:
                nframes = wf.getnframes()
                data = wf.readframes(nframes)
                fmt = "<h" if wf.getsampwidth() == 2 else "<b"
                samples = struct.unpack(fmt * nframes, data)
                if wf.getnchannels() > 1:
                    samples = samples[::wf.getnchannels()]  # mono
                return np.array(samples, dtype=float)
        except Exception as e:
            logger.error(f"Error leyendo {path}: {e}")
            return None

    def _load_from_bytes(self, data: bytes) -> Optional[np.ndarray]:
        """Carga audio desde bytes."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(data)
            tmp_path = f.name
        result = self._load_from_file(tmp_path)
        import os
        os.unlink(tmp_path)
        return result

    def _record_microphone(self, duration: float = 3.0) -> Optional[np.ndarray]:
        """
        Graba desde el micrófono usando parecord/sox como fallback
        si pyaudio no está disponible.
        """
        # Intentar con pyaudio
        try:
            import pyaudio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS,
                           rate=RATE, input=True,
                           frames_per_buffer=CHUNK)

            frames = []
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            audio_data = b''.join(frames)
            samples = np.frombuffer(audio_data, dtype=np.int16).astype(float)
            return samples
        except ImportError:
            pass

        # Fallback: arecord
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                tmp = f.name
            subprocess.run(
                ["arecord", "-d", str(int(duration)), "-f", "cd", "-t", "wav", tmp],
                capture_output=True, timeout=int(duration) + 5
            )
            result = self._load_from_file(tmp)
            import os
            os.unlink(tmp)
            return result
        except Exception as e:
            logger.error(f"Error grabando audio: {e}")
            return None

    # ─── Análisis de audio ────────────────────────────────────

    def analyze(self, audio: np.ndarray, sample_rate: int = 44100) -> AudioFeatures:
        """
        Analiza características del audio.
        
        Args:
            audio: Array 1D de samples float
            sample_rate: Frecuencia de muestreo
        
        Returns:
            AudioFeatures con análisis completo
        """
        feat = AudioFeatures()
        if audio is None or len(audio) == 0:
            return feat

        feat.sample_rate = sample_rate
        feat.duration = len(audio) / sample_rate
        feat.n_channels = 1

        # Volumen
        feat.rms_energy = float(np.sqrt(np.mean(audio ** 2)))
        feat.peak_amplitude = float(np.max(np.abs(audio)))

        # Silencio
        silence_threshold = feat.rms_energy * 0.1
        if feat.rms_energy > 0:
            feat.silence_ratio = float(np.mean(np.abs(audio) < silence_threshold))

        # Análisis por fragmentos
        frag_size = int(sample_rate * self.config.fragment_size_ms / 1000)
        if frag_size < 1:
            frag_size = sample_rate // 100  # 10ms

        feat.fragments = []
        for i in range(0, len(audio), frag_size):
            frag = audio[i:i + frag_size]
            if len(frag) < 2:
                continue
            f_rms = float(np.sqrt(np.mean(frag ** 2)))
            f_peak = float(np.max(np.abs(frag)))
            t = i / sample_rate
            feat.fragments.append({
                "time": round(t, 3),
                "rms": f_rms,
                "peak": f_peak,
                "energy_class": self._classify_energy(f_rms),
            })

        # Frecuencia dominante (FFT simple)
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)
        magnitudes = np.abs(fft)

        if len(magnitudes) > 0:
            dominant_idx = np.argmax(magnitudes[1:]) + 1  # skip DC
            feat.dominant_frequency = float(freqs[dominant_idx])

            # Spectral centroid
            if np.sum(magnitudes) > 0:
                feat.spectral_centroid = float(
                    np.sum(freqs * magnitudes) / np.sum(magnitudes)
                )

        # Tempo (estimación simple)
        # Detectar beats por picos de energía
        energy = np.array([f["rms"] for f in feat.fragments])
        if len(energy) > 5:
            energy_mean = np.mean(energy)
            energy_std = np.std(energy)
            threshold = energy_mean + energy_std * 0.5
            peaks = []
            for i in range(1, len(energy) - 1):
                if energy[i] > threshold and energy[i] > energy[i-1] and energy[i] > energy[i+1]:
                    peaks.append(i)

            if len(peaks) > 1:
                # Tiempo entre picos
                frag_duration = feat.fragments[1]["time"] - feat.fragments[0]["time"]
                intervals = np.diff([feat.fragments[p]["time"] for p in peaks])
                mean_interval = np.mean(intervals)
                if mean_interval > 0:
                    feat.tempo_bpm = round(60.0 / mean_interval, 1)
                feat.beats = [feat.fragments[p]["time"] for p in peaks]

        return feat

    def _classify_energy(self, rms: float) -> str:
        """Clasifica el nivel de energía."""
        if rms < 0.01:
            return "silencio"
        elif rms < 0.05:
            return "bajo"
        elif rms < 0.15:
            return "medio"
        elif rms < 0.3:
            return "alto"
        else:
            return "máximo"

    # ─── Visualización ────────────────────────────────────────

    def audio_to_ascii(self, audio: np.ndarray, sample_rate: int = 44100,
                        style: str = "waveform") -> str:
        """
        Convierte audio a visualización ASCII.
        
        Estilos:
          - waveform: forma de onda simple
          - spectrum: espectro de frecuencias
          - beats: patrón de beats/ritmo
          - energy: barras de energía por tiempo
        """
        feat = self.analyze(audio, sample_rate)

        if style == "waveform":
            return self._render_waveform(audio)
        elif style == "spectrum":
            return self._render_spectrum(audio, sample_rate)
        elif style == "beats":
            return self._render_beats(feat)
        elif style == "energy":
            return self._render_energy(feat)
        else:
            return self._render_waveform(audio)

    def _render_waveform(self, audio: np.ndarray) -> str:
        """Representación de forma de onda."""
        w = self.config.ascii_width
        h = self.config.ascii_height

        # Downsample
        chunk = max(1, len(audio) // w)
        segments = []
        for i in range(w):
            start = i * chunk
            end = start + chunk
            seg = audio[start:end]
            if len(seg) == 0:
                segments.append(0.0)
            else:
                segments.append(float(np.max(np.abs(seg))))

        # Normalizar
        max_val = max(segments) if segments else 1
        if max_val > 0:
            segments = [s / max_val for s in segments]

        # Renderizar
        lines = []
        for row in range(h - 1, -1, -1):
            threshold = (row + 0.5) / h
            line = ""
            for val in segments:
                if val > threshold:
                    # Diferentes caracteres según altura
                    if row > h * 0.7:
                        line += "█"
                    elif row > h * 0.4:
                        line += "▓"
                    elif row > h * 0.15:
                        line += "▒"
                    else:
                        line += "░"
                else:
                    line += " "
            lines.append(line)

        # Añadir eje de tiempo
        lines.append("─" * w)
        return "\n".join(lines)

    def _render_spectrum(self, audio: np.ndarray, sample_rate: int) -> str:
        """Espectro de frecuencias."""
        w = self.config.ascii_width
        h = self.config.ascii_height

        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)
        magnitudes = np.abs(fft)

        # Log scale para frecuencias y amplitudes
        mag_db = 20 * np.log10(magnitudes + 1e-10)

        # Dividir en bands logarítmicas
        bands = w
        band_size = len(mag_db) // bands
        if band_size < 1:
            band_size = 1
            bands = len(mag_db)

        band_mags = []
        for i in range(bands):
            start = i * band_size
            end = start + band_size
            band = mag_db[start:end]
            band_mags.append(float(np.mean(band) if len(band) > 0 else 0))

        # Normalizar
        min_mag, max_mag = min(band_mags), max(band_mags)
        r = max_mag - min_mag
        if r > 0:
            band_mags = [(m - min_mag) / r for m in band_mags]

        chars = " ▁▂▃▄▅▆▇█"
        line = ""
        for val in band_mags:
            idx = min(int(val * (len(chars) - 1)), len(chars) - 1)
            line += chars[idx]

        # Etiquetas de frecuencia
        n_labels = 5
        labels = []
        for i in range(n_labels):
            f = freqs[int(i * len(freqs) / n_labels)]
            pos = int(i * bands / n_labels)
            labels.append((pos, f"{f:.0f}Hz"))
        
        return f"{line}\n" + " ".join(f"{lbl:>8s}" for _, lbl in labels[:5])

    def _render_beats(self, feat: AudioFeatures) -> str:
        """Patrón de ritmo visual."""
        w = self.config.ascii_width

        if not feat.beats or feat.duration == 0:
            return "⏸️ No se detectaron beats"

        # Línea de tiempo de beats
        beat_positions = set()
        for b in feat.beats:
            pos = int((b / feat.duration) * w)
            beat_positions.add(pos)

        line = ""
        for i in range(w):
            if i in beat_positions:
                line += "█"
            elif i % 10 == 0:
                line += "│"
            else:
                line += "·"

        info = (
            f"🎵 Tempo: {feat.tempo_bpm:.0f} BPM | "
            f"Beats: {len(feat.beats)} | "
            f"Duración: {feat.duration:.1f}s"
        )
        return f"{info}\n{line}"

    def _render_energy(self, feat: AudioFeatures) -> str:
        """Barras de energía por fragmento."""
        w = self.config.ascii_width
        h = self.config.ascii_height

        fragments = feat.fragments
        if not fragments:
            return "⏸️ Sin datos"

        # Downsample a w columnas
        step = max(1, len(fragments) // w)
        energy_bars = []
        for i in range(0, len(fragments), step):
            batch = fragments[i:i + step]
            energy_bars.append(max(f["rms"] for f in batch))

        # Normalizar
        max_e = max(energy_bars) if energy_bars else 1
        if max_e > 0:
            energy_bars = [e / max_e for e in energy_bars]

        chars = " ▁▂▃▄▅▆▇█"
        line = ""
        for val in energy_bars:
            idx = min(int(val * (len(chars) - 1)), len(chars) - 1)
            line += chars[idx]

        info = (
            f"🔊 RMS: {feat.rms_energy:.3f} | "
            f"Pico: {feat.peak_amplitude:.1f} | "
            f"Silencio: {feat.silence_ratio:.0%}"
        )
        return f"{info}\n{line}"

    # ─── Pipeline completo ────────────────────────────────────

    def process_audio(self, source, style: str = "waveform",
                      sample_rate: int = 44100) -> dict:
        """
        Pipeline completo: carga → analiza → visualiza.
        
        Args:
            source: Ruta, bytes, o None (grabar)
            style: Estilo de visualización
            sample_rate: Frecuencia de muestreo
        
        Returns:
            Dict con análisis y visualización
        """
        audio = self.load_audio(source)
        if audio is None:
            return {"error": "No se pudo cargar el audio"}

        feat = self.analyze(audio, sample_rate)
        ascii_art = self.audio_to_ascii(audio, sample_rate, style)

        result = {
            "features": {
                "duration": feat.duration,
                "sample_rate": feat.sample_rate,
                "rms_energy": round(feat.rms_energy, 4),
                "peak_amplitude": round(feat.peak_amplitude, 2),
                "silence_ratio": round(feat.silence_ratio, 3),
                "dominant_frequency_hz": round(feat.dominant_frequency, 1),
                "tempo_bpm": feat.tempo_bpm,
                "n_beats": len(feat.beats),
                "transcription": feat.transcription,
            },
            "visualization": {
                "style": style,
                "ascii_art": ascii_art,
            },
            "fragments": feat.fragments[:200],  # limitar
        }
        return result

    def record_and_visualize(self, duration: float = 3.0,
                              style: str = "waveform") -> dict:
        """Graba audio del micrófono y lo visualiza."""
        audio = self._record_microphone(duration)
        if audio is None:
            return {"error": "No se pudo grabar audio"}
        return self.process_audio(audio, style=style, sample_rate=16000)


# ─── CLI ───────────────────────────────────────────────────────

def cli():
    """Interfaz CLI simple."""
    import sys
    if len(sys.argv) < 2:
        print("🦁 Synesthesia — Sinestesia artificial")
        print("Uso: python3 synesthesia.py <comando> [args]")
        print("\nComandos:")
        print("  visualize <archivo.wav> [style]  — Visualizar audio")
        print("  record [duration] [style]        — Grabar y visualizar")
        print("\nEstilos: waveform, spectrum, beats, energy")
        return

    cmd = sys.argv[1]
    sp = SynesthesiaProcessor()

    if cmd == "visualize":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        style = sys.argv[3] if len(sys.argv) > 3 else "waveform"
        if not path:
            print("Uso: synesthesia.py visualize <archivo.wav> [style]")
            return
        result = sp.process_audio(path, style=style)
        if "error" in result:
            print(f"❌ {result['error']}")
            return
        print(result["visualization"]["ascii_art"])
        print()
        for k, v in result["features"].items():
            if v and k != "transcription":
                print(f"  {k}: {v}")

    elif cmd == "record":
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
        style = sys.argv[3] if len(sys.argv) > 3 else "waveform"
        print(f"🎤 Grabando {duration}s...")
        result = sp.record_and_visualize(duration, style)
        if "error" in result:
            print(f"❌ {result['error']}")
            return
        print(result["visualization"]["ascii_art"])
        print()
        for k, v in result["features"].items():
            if v:
                print(f"  {k}: {v}")


if __name__ == "__main__":
    cli()

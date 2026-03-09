import { useMemo, useState, type ReactNode } from "react";
import {
  angle,
  calculateLineAndNeutralCurrents,
  type Complex,
  magnitude,
  resistiveImpedanceFromPower,
} from "./core/physics";

const V_PHASE_RMS = 230;
const WAVE_SAMPLES = 220;
const WAVE_CYCLES = 1.25;
const GRID_MAX_AMP = 20;
const CURRENT_TICKS_A = [5, 10, 15, 20];
const PERIOD_MS = 20;
const MAX_PHASE_POWER_W = 2000;
const MAX_DELTA_POWER_W = 3000;
const IMAGE_URL = "/3fas.jpg";

const LOAD_COLORS = {
  p1: "#ff4d4d",
  p2: "#4ddc6f",
  p3: "#4f8fff",
  p12: "#ffd84d",
  p23: "#ff5ed4",
  p31: "#ff9b3d",
};

function ampLabel(value: number): string {
  return `${value.toFixed(2)} A`;
}

function deg(rad: number): number {
  return (rad * 180) / Math.PI;
}

const FIXED_MAX_AMP = GRID_MAX_AMP;

export default function App() {
  const [p1, setP1] = useState(0);
  const [p2, setP2] = useState(0);
  const [p3, setP3] = useState(0);
  const [p12, setP12] = useState(0);
  const [p23, setP23] = useState(0);
  const [p31, setP31] = useState(0);

  const currents = useMemo(() => {
    const yImpedances: [Complex | null, Complex | null, Complex | null] = [
      resistiveImpedanceFromPower(p1, V_PHASE_RMS),
      resistiveImpedanceFromPower(p2, V_PHASE_RMS),
      resistiveImpedanceFromPower(p3, V_PHASE_RMS),
    ];

    const vLineRms = V_PHASE_RMS * Math.sqrt(3);
    const deltaImpedances: [Complex | null, Complex | null, Complex | null] = [
      resistiveImpedanceFromPower(p12, vLineRms),
      resistiveImpedanceFromPower(p23, vLineRms),
      resistiveImpedanceFromPower(p31, vLineRms),
    ];

    return calculateLineAndNeutralCurrents({
      yImpedances,
      deltaImpedances,
      voltageRms: V_PHASE_RMS,
    });
  }, [p1, p2, p3, p12, p23, p31]);

  const [i1, i2, i3] = currents.lineCurrents;
  const inNeutral = currents.neutralCurrent;

  function resetLoads(): void {
    setP1(0);
    setP2(0);
    setP3(0);
    setP12(0);
    setP23(0);
    setP31(0);
  }

  return (
    <main className="page">
      <section className="hero-card">
        <p className="kicker">Trefas Web Prototype</p>
        <h1>Structured Three-Phase Simulator</h1>
        <p>
          New web-native shell using a pure TypeScript physics engine. Start by
          adjusting active loads and verify current phasors.
        </p>
      </section>

      <section className="panel-grid">
        <article className="panel panel-controls">
          <div className="controls-layout">
            <div>
              <h2>Phase Loads (Y)</h2>
              <LoadSlider label={<PowerLabel base="P" sub="1" suffix=" (L1-N)" />} value={p1} onChange={setP1} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p1} />
              <LoadSlider label={<PowerLabel base="P" sub="2" suffix=" (L2-N)" />} value={p2} onChange={setP2} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p2} />
              <LoadSlider label={<PowerLabel base="P" sub="3" suffix=" (L3-N)" />} value={p3} onChange={setP3} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p3} />

              <h2>Line Loads (Delta)</h2>
              <LoadSlider label={<PowerLabel base="P" sub="12" suffix=" (L1-L2)" />} value={p12} onChange={setP12} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p12} />
              <LoadSlider label={<PowerLabel base="P" sub="23" suffix=" (L2-L3)" />} value={p23} onChange={setP23} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p23} />
              <LoadSlider label={<PowerLabel base="P" sub="31" suffix=" (L3-L1)" />} value={p31} onChange={setP31} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p31} />
              <button type="button" className="reset-btn" onClick={resetLoads}>Reset (all P=0)</button>

              <p className="scale-note">Resulting currents</p>
              <div className="current-strip instrument-strip">
                <CurrentChip symbolBase="I" symbolSub="1" amp={magnitude(i1)} phaseDeg={deg(angle(i1))} />
                <CurrentChip symbolBase="I" symbolSub="2" amp={magnitude(i2)} phaseDeg={deg(angle(i2))} />
                <CurrentChip symbolBase="I" symbolSub="3" amp={magnitude(i3)} phaseDeg={deg(angle(i3))} />
                <CurrentChip symbolBase="I" symbolSub="N" amp={magnitude(inNeutral)} phaseDeg={deg(angle(inNeutral))} strong />
              </div>
            </div>

            <figure className="circuit-image-wrap">
              <img src={IMAGE_URL} alt="Three-phase circuit diagram" className="circuit-image" />
            </figure>
          </div>
        </article>

        <article className="panel panel-viz-combined">
          <h2>Phasor + Waveform (Linked)</h2>
          <LinkedDiagrams currents={[i1, i2, i3, inNeutral]} maxAmp={FIXED_MAX_AMP} />
        </article>
      </section>
    </main>
  );
}

function LoadSlider(props: {
  label: ReactNode;
  value: number;
  max: number;
  color: string;
  onChange: (v: number) => void;
}) {
  return (
    <label className="slider-row">
      <span className="symbol-wrap" style={{ color: props.color }}>{props.label}</span>
      <input
        type="range"
        min={0}
        max={props.max}
        step={10}
        value={props.value}
        style={{ accentColor: props.color }}
        onChange={(e) => props.onChange(Number(e.target.value))}
      />
      <strong style={{ color: props.color }}>{props.value.toFixed(0)} W</strong>
    </label>
  );
}

function PowerLabel(props: { base: string; sub: string; suffix?: string }) {
  return (
    <>
      <em>{props.base}</em>
      <sub>{props.sub}</sub>
      {props.suffix ?? ""}
    </>
  );
}

function vectorEnd(current: Complex, center: number, radius: number, maxAmp: number): [number, number] {
  const amp = magnitude(current);
  const ang = angle(current);
  const r = (amp / maxAmp) * radius;
  return [center + r * Math.cos(ang), center - r * Math.sin(ang)];
}

function LinkedDiagrams(props: { currents: [Complex, Complex, Complex, Complex]; maxAmp: number }) {
  const pane = 340;
  const gap = 24;
  const width = pane * 2 + gap;
  const height = pane;

  const centerX = pane / 2;
  const centerY = pane / 2;
  const radius = 116;

  const waveOffsetX = pane + gap;
  const plotLeft = waveOffsetX + 36;
  const plotRight = waveOffsetX + pane - 12;
  const plotTop = 32;
  const plotBottom = pane - 32;
  const plotWidth = plotRight - plotLeft;
  const yScale = radius / props.maxAmp;

  const colors = ["#ff7b78", "#7ef0a4", "#7ec6ff", "#fff0ac"];
  const labels = [
    { base: "I", sub: "1" },
    { base: "I", sub: "2" },
    { base: "I", sub: "3" },
    { base: "I", sub: "N" },
  ];
  const markers = ["arrow-l1", "arrow-l2", "arrow-l3", "arrow-ln"];
  const scaleFractions = CURRENT_TICKS_A.map((tick) => tick / props.maxAmp);
  const yTicks = [-20, -15, -10, -5, 0, 5, 10, 15, 20];
  const xTicksMs = [0, 5, 10, 15, 20, 25];

  function waveformPath(current: Complex): string {
    const amp = magnitude(current);
    const phase = angle(current);
    const xScale = plotWidth / (WAVE_SAMPLES - 1);
    let path = "";
    for (let i = 0; i < WAVE_SAMPLES; i += 1) {
      const t = (i / (WAVE_SAMPLES - 1)) * (Math.PI * 2) * WAVE_CYCLES;
      const x = plotLeft + i * xScale;
      const y = centerY - amp * Math.sin(t + phase) * yScale;
      path += i === 0 ? `M ${x.toFixed(2)} ${y.toFixed(2)}` : ` L ${x.toFixed(2)} ${y.toFixed(2)}`;
    }
    return path;
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="viz-svg viz-linked" role="img" aria-label="Linked phasor and waveform diagrams">
      <defs>
        <marker id="arrow-l1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ff7b78" />
        </marker>
        <marker id="arrow-l2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7ef0a4" />
        </marker>
        <marker id="arrow-l3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7ec6ff" />
        </marker>
        <marker id="arrow-ln" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#fff0ac" />
        </marker>
      </defs>

      {scaleFractions.map((fraction) => (
        <circle key={fraction} cx={centerX} cy={centerY} r={radius * fraction} className="phasor-grid" />
      ))}
      <line x1={centerX - radius} y1={centerY} x2={centerX + radius} y2={centerY} className="phasor-axis" />
      <line x1={centerX} y1={centerY - radius} x2={centerX} y2={centerY + radius} className="phasor-axis" />
      {CURRENT_TICKS_A.map((tick) => {
        const y = centerY - (tick / props.maxAmp) * radius;
        return (
          <g key={`tick-${tick}`}>
            <line x1={centerX - 4} y1={y} x2={centerX + 4} y2={y} className="phasor-axis" />
            <text x={centerX + 8} y={y + 4} className="viz-scale-label">{tick} A</text>
          </g>
        );
      })}
      <text x={centerX + 8} y={centerY - radius - 8} className="viz-scale-label">Current scale</text>

      <line x1={plotLeft} y1={plotTop} x2={plotLeft} y2={plotBottom} className="phasor-axis" />
      <line x1={plotLeft} y1={centerY} x2={plotRight} y2={centerY} className="phasor-axis" />
      {yTicks.map((tick) => {
        const y = centerY - (tick / props.maxAmp) * radius;
        return (
          <g key={`y-${tick}`}>
            <line x1={plotLeft} y1={y} x2={plotRight} y2={y} className="wave-grid" />
            <text x={waveOffsetX + 4} y={y + 4} className="viz-scale-label">{tick} A</text>
          </g>
        );
      })}
      {xTicksMs.map((tickMs) => {
        const x = plotLeft + (tickMs / (WAVE_CYCLES * PERIOD_MS)) * plotWidth;
        return (
          <g key={`x-${tickMs}`}>
            <line x1={x} y1={plotTop} x2={x} y2={plotBottom} className="wave-grid" />
            <text x={x - 10} y={height - 8} className="viz-scale-label">{tickMs} ms</text>
          </g>
        );
      })}

      {props.currents.map((current, idx) => {
        const [x2, y2] = vectorEnd(current, centerX, radius, props.maxAmp);
        const t0y = centerY - magnitude(current) * Math.sin(angle(current)) * yScale;
        return (
          <g key={`phase-${idx}`}>
            <line x1={x2} y1={y2} x2={plotLeft} y2={t0y} stroke={colors[idx]} className="phasor-dashed" />
            <line
              x1={centerX}
              y1={centerY}
              x2={x2}
              y2={y2}
              stroke={colors[idx]}
              strokeWidth={2}
              markerEnd={`url(#${markers[idx]})`}
            />
            <text x={x2 + 6} y={y2 - 6} fill={colors[idx]} className="viz-label">
              <tspan fontStyle="italic">{labels[idx].base}</tspan>
              <tspan baselineShift="sub" fontSize="9">{labels[idx].sub}</tspan>
            </text>
            <path d={waveformPath(current)} fill="none" stroke={colors[idx]} strokeWidth={idx === 3 ? 3 : 2} />
            <circle cx={plotLeft} cy={t0y} r={3} fill={colors[idx]} />
          </g>
        );
      })}

      <text x={plotLeft + 4} y={plotBottom + 16} className="viz-scale-label">t=0</text>
    </svg>
  );
}

function CurrentChip(props: {
  symbolBase: string;
  symbolSub: string;
  amp: number;
  phaseDeg: number;
  strong?: boolean;
}) {
  return (
    <div className={`current-chip ${props.strong ? "strong" : ""}`}>
      <span className="name"><em>{props.symbolBase}</em><sub>{props.symbolSub}</sub></span>
      <span className="amp">{ampLabel(props.amp)}</span>
      <span className="angle">{props.phaseDeg.toFixed(1)}°</span>
    </div>
  );
}

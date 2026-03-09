# Trefas Web App

A standalone web-native prototype (Vite + React + TypeScript) for the three-phase simulator.

## Why this folder

This app is isolated from the Python/Pygame project so you can iterate on web UX and architecture independently.

## Structure

- `src/core/physics.ts`: Pure three-phase current calculator (complex arithmetic).
- `src/App.tsx`: UI shell and state wiring for load sliders and calculated currents.
- `src/styles.css`: Visual design and responsive layout.

## Run locally

1. Install Node.js 20+ (includes `npm`).
2. In this folder, run:

```bash
npm install
npm run dev
```

3. Open the local URL shown by Vite.

## Next milestones

- Add phasor diagram and waveform plots in SVG.
- Move UI state to a dedicated store (e.g. Zustand).
- Add unit tests for `src/core/physics.ts`.
- Add import/export of scenario JSON.

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

## Deploy to GitHub Pages

This repo is configured to auto-deploy the web app from GitHub Actions.

1. Push to `main`.
2. In GitHub, open `Settings -> Pages`.
3. Set `Source` to `GitHub Actions`.
4. Wait for workflow `Deploy Web App to GitHub Pages` to finish.

Notes:
- The workflow file is `.github/workflows/deploy-pages.yml`.
- It builds from `src/trefas_web_app` and publishes `src/trefas_web_app/dist`.
- The Vite base path is set automatically to `/<repo-name>/` during deployment.

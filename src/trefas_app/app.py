import asyncio
import os
import sys

import pygame

from .gui import ThreePhaseGUI
from .simulation import ThreePhaseModel


def resource_path(relative_path):
    """Resolve assets independent of current working directory."""
    base_candidates = []

    if hasattr(sys, "_MEIPASS"):
        base_candidates.append(sys._MEIPASS)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    repo_root = os.path.dirname(src_dir)
    base_candidates.extend(
        [
            script_dir,
            src_dir,
            repo_root,
            os.path.join(repo_root, "assets", "runtime"),
            os.path.join(repo_root, "3fas-web"),
        ]
    )

    for base_path in base_candidates:
        candidate = os.path.join(base_path, relative_path)
        if os.path.exists(candidate):
            return candidate

    return os.path.join(script_dir, relative_path)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Trefas-simulator: Y-koppling")
    clock = pygame.time.Clock()

    model = ThreePhaseModel()
    ui = ThreePhaseGUI(1200, 800, model, resource_path)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        ui.update(events, dt)

        w, h = screen.get_size()
        if w != ui.w or h != ui.h:
            ui.update_layout(w, h)

        ui.draw(screen)
        pygame.display.flip()

        # Required on web builds to yield control back to browser event loop.
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


def run():
    asyncio.run(main())

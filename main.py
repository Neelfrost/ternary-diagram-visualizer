import math
import os
import sys

import pygame
from pygame.math import Vector2 as Vector2

# Fix imports
# https://stackoverflow.com/questions/40716346/windows-pyinstaller-error-failed-to-execute-script-when-app-clicked
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Checks if a point (p) is within a triangle (p0, p1, p2)
def isPointInTriangle(p, p0, p1, p2):
    area = (-p1[1] * p2[0] + p0[1] * (-p1[0] + p2[0]) + p0[0] * (p1[1] - p2[1]) + p1[0] * p2[1]) / 2
    sign = -1 if area < 0 else 1
    s = (p0[1] * p2[0] - p0[0] * p2[1] + (p2[1] - p0[1]) * p[0] + (p0[0] - p2[0]) * p[1]) * sign
    t = (p0[0] * p1[1] - p0[1] * p1[0] + (p0[1] - p1[1]) * p[0] + (p1[0] - p0[0]) * p[1]) * sign

    return s > 0 and t > 0 and (s + t) < 2 * area * sign


# Calculates the intercept required for a line to pass through point (x, y) while begin parallel to a line (ax + by + c = 0)
def parallelIntercept(a, b, x, y):
    return -a * x - b * y


# Calculates the coordinates for the point of intersection of two given lines (a1x + b1y + c1 = 0) and (a2x + b2y + c2 = 0)
def pointOfIntersection(a1, b1, c1, a2, b2, c2):
    x = (b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1)
    y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1)

    return x, y


# Calculates the length between two points (x1, y1) and (x2, y2)
def lengthBetween(x1, y1, x2, y2):
    length = math.sqrt(abs((y2 - y1) ** 2 - (x2 - x1) ** 2))
    return length


# Draws apexes
def drawLabels(canvas, font):
    apex = [
        font.render("A", True, (0, 255, 0)),
        font.render("B", True, (0, 0, 255)),
        font.render("C", True, (255, 0, 0)),
    ]

    canvas.blit(apex[0], apex[0].get_rect(center=(256, 48)))
    canvas.blit(apex[1], apex[1].get_rect(center=(16, 448)))
    canvas.blit(apex[2], apex[2].get_rect(center=(496, 448)))


def drawComposition(canvas, font, color, comp, x, y):
    text = font.render(str(comp), True, color)
    canvas.blit(text, text.get_rect(center=(x, y)))


def main():
    pygame.init()
    pygame.display.set_caption("Ternary Phase Diagram / Composition Triangle Simulator")
    icon = pygame.image.load(resource_path("icon.png"))
    pygame.display.set_icon(icon)

    font = pygame.font.SysFont("arial", 24)
    guideFont = pygame.font.SysFont("arial", 16)
    canvas = pygame.display.set_mode((512, 512))
    clock = pygame.time.Clock()

    # For follow toggle
    toggle = False

    guide = guideFont.render(
        "Left click to disable mouse follow | Right click to enable mouse follow", True, (255, 255, 255)
    )

    # Apexes of the triangle
    p0 = (32, 448)
    p1 = (256, 64)
    p2 = (480, 448)

    while True:
        # Clear canvas
        canvas.fill((0, 0, 0))
        # Draw instructions
        canvas.blit(guide, guide.get_rect(center=(256, 16)))

        if pygame.mouse.get_pressed() == (1, 0, 0):
            toggle = True
        elif pygame.mouse.get_pressed() == (0, 0, 1):
            toggle = False

        if not toggle:
            mousePos = pygame.mouse.get_pos()

        # Triangle
        pygame.draw.line(canvas, (255, 255, 255), p0, p2)
        pygame.draw.line(canvas, (255, 255, 255), p0, p1)
        pygame.draw.line(canvas, (255, 255, 255), p1, p2)

        # Triangle grid
        # Horizontal
        for y in range(1, 10):
            tempX1, tempY1 = pointOfIntersection(0, 1, -448 + y * 38.8, 12, 7, -3520)
            tempX2, tempY2 = pointOfIntersection(0, 1, -448 + y * 38.8, 12, -7, -2624)
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))
        # Parallel to left
        for x in range(1, 10):
            tempX1, tempY1 = pointOfIntersection(0, 1, -448, 12, 7, parallelIntercept(12, 7, 32 + x * 44.8, 448))
            tempX2, tempY2 = pointOfIntersection(12, -7, -2624, 12, 7, parallelIntercept(12, 7, 32 + x * 44.8, 448))
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))
        # Parallel to right
        for x in range(1, 10):
            tempX1, tempY1 = pointOfIntersection(0, 1, -448, 12, -7, parallelIntercept(12, -7, 480 - x * 44.8, 448))
            tempX2, tempY2 = pointOfIntersection(12, 7, -3520, 12, -7, parallelIntercept(12, -7, 480 - x * 44.8, 448))
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))

        drawLabels(canvas, font)

        # Composition lines
        if isPointInTriangle(mousePos, p0, p1, p2):
            # Composition of A
            x1, y1 = pointOfIntersection(0, 1, -mousePos[1], 12, -7, -2624)
            compA = round(lengthBetween(x1, y1, p2[0], p2[1]) / lengthBetween(p1[0], p1[1], p2[0], p2[1]), 2)
            # Draw Composition
            drawComposition(canvas, font, (0, 255, 0), compA, x1 + 32, y1)
            # Draw line
            pygame.draw.line(canvas, (0, 255, 0), (mousePos[0], mousePos[1]), (x1, y1), width=2)

            # Composition of B
            x2, y2 = pointOfIntersection(12, 7, -3520, 12, -7, parallelIntercept(12, -7, mousePos[0], mousePos[1]))
            compB = round(lengthBetween(x2, y2, p1[0], p1[1]) / lengthBetween(p0[0], p0[1], p1[0], p1[1]), 2)
            # Draw Composition
            drawComposition(canvas, font, (0, 0, 255), compB, x2 - 32, y2)
            # Draw line
            pygame.draw.line(canvas, (0, 0, 255), (mousePos[0], mousePos[1]), (x2, y2), width=2)

            # Composition of C
            x3, y3 = pointOfIntersection(0, 1, -448, 12, 7, parallelIntercept(12, 7, mousePos[0], mousePos[1]))
            compC = round(lengthBetween(x3, y3, p0[0], p0[1]) / lengthBetween(p0[0], p0[1], p2[0], p2[1]), 2)
            # Draw Composition
            drawComposition(canvas, font, (255, 0, 0), compC, x3, y3 + 32)
            # Draw line
            pygame.draw.line(
                canvas,
                (255, 0, 0),
                (mousePos[0], mousePos[1]),
                (x3, y3),
                width=2,
            )
            # Draw cursor, Final composition of Alloy
            pygame.draw.circle(canvas, (255, 255, 255), mousePos, 3, width=0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()

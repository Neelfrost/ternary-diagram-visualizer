import math
import os
import sys

import pygame

RED = (224, 108, 117)
GREEN = (152, 195, 121)
BLUE = (96, 175, 238)
WHITE = (220, 223, 228)
BLACK = (40, 44, 52)

# from pygame.math import Vector2 as Vector2

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


# Calculates the intercept required for a line to pass through point (x, y)
# while begin parallel to a line (ax + by + c = 0)
def parallelIntercept(a, b, x, y):
    return -a * x - b * y


# Calculates the intercept required for a line to pass through point (x, y)
# while begin perpendicular to a line (ax + by + c = 0)
def perpendicularIntercept(a, b, x, y):
    return -(b * x - a * y)


# Calculates the coordinates for the point of intersection of two given lines
# (a1x + b1y + c1 = 0) and (a2x + b2y + c2 = 0)
def pointOfIntersection(a1, b1, c1, a2, b2, c2):
    x = (b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1)
    y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1)

    return x, y


# Calculates the length between two points (x1, y1) and (x2, y2)
def lengthBetween(x1, y1, x2, y2):
    length = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    return length


# Draws apexes
def drawLabels(canvas, font, p0, p1, p2):
    labelOffset = 16

    apex = [
        font.render("A", True, GREEN),
        font.render("B", True, BLUE),
        font.render("C", True, RED),
    ]

    canvas.blit(apex[0], apex[0].get_rect(center=(p0[0], p0[1] - labelOffset)))
    canvas.blit(apex[1], apex[1].get_rect(center=(p1[0] - labelOffset, p1[1] + labelOffset)))
    canvas.blit(apex[2], apex[2].get_rect(center=(p2[0] + labelOffset, p2[1] + labelOffset)))


# Draws text 'comp' with font 'font' on canvas centered at x,y
def drawComposition(canvas, font, color, comp, x, y):
    text = font.render(str(comp), True, color)
    canvas.blit(text, text.get_rect(center=(x, y)))


# How lines are drawn:
# For a unique line to be drawn, we require either a point + slope, or 2 points. Moreover, pygame requires the
# specification of 2 points for a line to be drawn.
# Assuming the first point is the current mouse position, we calculate the 2nd point as follows:
# Get the parameters of the line passing through the mouse postion (while being parallel to some line say, a1x + b1y +
# c1 = 0). The parameters of this line would be, a1, b1, and parallelIntercept(a1, b1, mousepositionX,
# mousepositionY).
# Now that we have the parameters of this line, we can calculate the 2nd point using pointOfIntersection between this
# line and some other line say, a2x + b2y + c2 = 0, using pointOfIntersection(a1, b1, c1, a2, b2, c2).


def main():
    pygame.init()
    pygame.display.set_caption("Ternary Phase Diagram Simulator")
    icon = pygame.image.load(resource_path("icon.png"))
    pygame.mouse.set_cursor(pygame.cursors.broken_x)
    pygame.display.set_icon(icon)

    compositionFont = pygame.font.SysFont("arial", 24)
    guideFont = pygame.font.SysFont("arial", 18)
    canvas = pygame.display.set_mode((650, 650), pygame.NOFRAME)
    clock = pygame.time.Clock()

    # For follow toggle
    toggle = False
    # To change mode
    mode = True

    # Instruction text
    guideText = guideFont.render(
        "Left click to disable mouse follow | Right click to enable mouse follow | Press 'm' to toggle modes",
        True,
        WHITE,
    )
    closeText = guideFont.render("Press 'ESC' to close", True, WHITE)

    # Composition values
    compA, compB, compC = 0, 0, 0

    # Shift apexes by offset
    # center around apex p1
    offset = canvas.get_size()[0] / 2 - 256

    # Side length, altitude of triangle
    sideLength = 500
    altitude = math.sin(math.pi / 3) * sideLength

    # Calculate apexes of the triangle using apex p1
    p0 = (256 - math.sqrt((sideLength ** 2) - (altitude ** 2)) + offset, 64 + altitude + offset)
    p1 = (256 + offset, 64 + offset)
    p2 = (p0[0] + sideLength, 64 + altitude + offset)

    # Equations (parameters) of the lines that makeup the triangle
    # p0-p1 (left): (p1[1]-p0[1]) * x - (p1[0]-p0[0]) * y - p0[1] * (p1[0] - p0[0]) - p0[0] * (p1[1] - p0[1])
    # p1-p2 (right): (p2[1]-p1[1]) * x - (p2[0]-p1[0]) * y - p1[1] * (p2[0] - p1[0]) - p1[0] * (p2[1] - p1[1])
    # p0-p2 (bottom): y - p0[1]
    a1 = p1[1] - p0[1]
    b1 = -(p1[0] - p0[0])
    c1 = p0[1] * (p1[0] - p0[0]) - p0[0] * (p1[1] - p0[1])
    a2 = p2[1] - p1[1]
    b2 = -(p2[0] - p1[0])
    c2 = p1[1] * (p2[0] - p1[0]) - p1[0] * (p2[1] - p1[1])
    a3 = 0
    b3 = 1
    c3 = -p0[1]

    while True:
        # Clear canvas
        canvas.fill((0, 0, 0))

        # Set toggle text
        toggleText = guideFont.render(
            "Following" if not toggle else "Not Following", True, GREEN if not toggle else RED
        )

        # Set mode text
        modeText = guideFont.render(
            "Using Parallel Method" if mode else "Using Altitude Method", True, GREEN if mode else BLUE
        )

        # Draw instructions
        canvas.blit(guideText, guideText.get_rect(center=(canvas.get_size()[0] / 2, 16)))
        canvas.blit(closeText, closeText.get_rect(center=(canvas.get_size()[0] / 2, canvas.get_size()[0] - 16)))
        canvas.blit(toggleText, toggleText.get_rect(center=(canvas.get_size()[0] / 2, 48)))
        canvas.blit(modeText, modeText.get_rect(center=(canvas.get_size()[0] / 2, 80)))

        # Draw apexes
        drawLabels(canvas, compositionFont, p1, p0, p2)

        if not toggle:
            mousePos = pygame.mouse.get_pos()

        # Draw triangle
        pygame.draw.line(canvas, WHITE, p0, p2)
        pygame.draw.line(canvas, WHITE, p0, p1)
        pygame.draw.line(canvas, WHITE, p1, p2)

        # Draw inner triangle grid
        for i in range(1, 10):
            # Parallel to bottom
            tempX1, tempY1 = pointOfIntersection(0, 1, -p0[1] + i * altitude / 10, a1, b1, c1)

            tempX2, tempY2 = pointOfIntersection(a3, b3, c3 + i * altitude / 10, a2, b2, c2)
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))

            # Parallel to left
            tempX1, tempY1 = pointOfIntersection(
                a3, b3, c3, a1, b1, parallelIntercept(a1, b1, p0[0] + i * sideLength / 10, p0[1])
            )
            tempX2, tempY2 = pointOfIntersection(
                a2, b2, c2, a1, b1, parallelIntercept(a1, b1, p0[0] + i * sideLength / 10, p0[1])
            )
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))

            # Parallel to right
            tempX1, tempY1 = pointOfIntersection(
                a3, b3, c3, a2, b2, parallelIntercept(a2, b2, p2[0] - i * sideLength / 10, p0[1])
            )
            tempX2, tempY2 = pointOfIntersection(
                a1, b1, c1, a2, b2, parallelIntercept(a2, b2, p2[0] - i * sideLength / 10, p0[1])
            )
            pygame.draw.line(canvas, (100, 100, 100), (tempX1, tempY1), (tempX2, tempY2))

        # Composition lines
        if isPointInTriangle(mousePos, p0, p1, p2):
            if mode:
                # Mode 1
                # Composition of A
                # Length between point of intersection and apex C / length of side
                x1, y1 = pointOfIntersection(0, 1, -mousePos[1], a2, b2, c2)
                compA = round(lengthBetween(x1, y1, p2[0], p2[1]) / lengthBetween(p1[0], p1[1], p2[0], p2[1]), 2)
                # Draw composition
                drawComposition(canvas, compositionFont, GREEN, compA, x1 + 32, y1)
                # Draw line
                pygame.draw.line(canvas, GREEN, (mousePos[0], mousePos[1]), (x1, y1), width=2)

                # Composition of B
                # Length between point of intersection and apex A / length of side
                x2, y2 = pointOfIntersection(a1, b1, c1, a2, b2, parallelIntercept(a2, b2, mousePos[0], mousePos[1]))
                compB = round(lengthBetween(x2, y2, p1[0], p1[1]) / lengthBetween(p0[0], p0[1], p1[0], p1[1]), 2)
                # Draw composition
                drawComposition(canvas, compositionFont, BLUE, compB, x2 - 32, y2)
                # Draw line
                pygame.draw.line(canvas, BLUE, (mousePos[0], mousePos[1]), (x2, y2), width=2)

                # Composition of C
                # Length between point of intersection and apex B / length of side
                x3, y3 = pointOfIntersection(0, 1, c3, a1, b1, parallelIntercept(a1, b1, mousePos[0], mousePos[1]))
                compC = round(lengthBetween(x3, y3, p0[0], p0[1]) / lengthBetween(p0[0], p0[1], p2[0], p2[1]), 2)
                # Draw composition
                drawComposition(canvas, compositionFont, RED, compC, x3, y3 + 32)
                # Draw line
                pygame.draw.line(
                    canvas,
                    RED,
                    (mousePos[0], mousePos[1]),
                    (x3, y3),
                    width=2,
                )
            else:
                # Mode 2
                # Composition of A, perpendicular to p0-p2, passing through mousePos
                # Length between point of intersection and mousePos / length of altitude
                x1, y1 = pointOfIntersection(1, 0, -mousePos[0], a3, b3, c3)
                compA = round(
                    lengthBetween(x1, y1, mousePos[0], mousePos[1]) / altitude,
                    2,
                )
                # Draw composition
                drawComposition(canvas, compositionFont, GREEN, compA, x1, y1 + 32)
                # Draw line
                pygame.draw.line(canvas, GREEN, (mousePos[0], mousePos[1]), (x1, y1), width=2)

                # Composition of B, perpendicular to p1-p2, passing through mousePos
                # Length between point of intersection and mousePos / length of altitude
                x2, y2 = pointOfIntersection(
                    b1, a1, perpendicularIntercept(a2, b2, mousePos[0], mousePos[1]), a2, b2, c2
                )
                compB = round(
                    lengthBetween(x2, y2, mousePos[0], mousePos[1]) / altitude,
                    2,
                )
                # Draw composition, perpendicular to p0-p1, passing through mousePos
                # Length between point of intersection and mousePos / length of altitude
                drawComposition(canvas, compositionFont, BLUE, compB, x2 + 32, y2)
                # Draw line
                pygame.draw.line(canvas, BLUE, (mousePos[0], mousePos[1]), (x2, y2), width=2)

                # Composition of C
                x3, y3 = pointOfIntersection(
                    b2, a2, perpendicularIntercept(a1, b1, mousePos[0], mousePos[1]), a1, b1, c1
                )
                compC = round(
                    lengthBetween(x3, y3, mousePos[0], mousePos[1]) / altitude,
                    2,
                )
                # Draw composition
                drawComposition(canvas, compositionFont, RED, compC, x3 - 32, y3)
                # Draw line
                pygame.draw.line(
                    canvas,
                    RED,
                    (mousePos[0], mousePos[1]),
                    (x3, y3),
                    width=2,
                )

            # Draw cursor, aka. the final composition of alloy
            pygame.draw.circle(canvas, WHITE, mousePos, 3, width=0)

            # Get toggle state
            if pygame.mouse.get_pressed() == (1, 0, 0):
                toggle = True
            elif pygame.mouse.get_pressed() == (0, 0, 1):
                toggle = False

        # Extra composition display
        drawComposition(canvas, compositionFont, GREEN, "A: " + str(compA), canvas.get_size()[0] - 100, 120)
        drawComposition(canvas, compositionFont, BLUE, "B: " + str(compB), canvas.get_size()[0] - 100, 160)
        drawComposition(canvas, compositionFont, RED, "C: " + str(compC), canvas.get_size()[0] - 100, 200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    mode = not mode
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()

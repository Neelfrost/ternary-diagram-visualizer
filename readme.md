# Background

Ternary systems are those having three components. Because of its unique geometric characteristics, an equilateral triangle the simplest means for plotting ternary composition.

For the purposes of phase equilibria, such an equilateral triangle is known as _composition triangle_ or _Gibbs' triangle_.

The three pure component metals are represented at the apexes, A, B, and C. Binary composition is represented along the edges, i.e., the binary systems AB, AC, and BC. And ternary alloys are represented within the area of the triangle.

To find the composition of the alloy at a point of we simply draw three lines from this point parallel to the sides of the triangle. E.g., to find the composition of A in the alloy, draw line parallel to side opposite of 100\% A. Where this line cuts the \% A axis, gives us the composition of A in the alloy.

# How to run

Download the compiled .exe from the releases or compile it yourself by cloning the repo. Then run the .exe to launch the simulator.

# How to compile

1. Install pyinstaller: `pip install pyinstaller`

2. Clone this repo: `git clone https://github.com/Neelfrost/ternary-phase-diagram-sim.git`

3. Cd into the directory: `cd .\ternary-phase-diagram-sim\`

4. Run: `pyinstaller.exe -F -w -i 'icon.ico' --add-binary 'icon.png;.' .\main.py`

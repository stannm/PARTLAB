import ezdxf
import math
import matplotlib.pyplot as plt

def analyze_dxf_file(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    perimeter = 0.0
    num_holes = 0

    for e in msp:
        if e.dxftype() == "LINE":
            start = e.dxf.start
            end = e.dxf.end
            length = math.dist(start, end)
            perimeter += length
        elif e.dxftype() == "CIRCLE":
            radius = e.dxf.radius
            perimeter += 2 * math.pi * radius
            num_holes += 1
        elif e.dxftype() == "ARC":
            angle = abs(e.dxf.end_angle - e.dxf.start_angle)
            arc_length = 2 * math.pi * e.dxf.radius * (angle / 360)
            perimeter += arc_length
        elif e.dxftype() == "LWPOLYLINE":
            points = e.get_points("xy")
            for i in range(len(points) - 1):
                perimeter += math.dist(points[i], points[i + 1])
            if e.closed and len(points) > 2:
                perimeter += math.dist(points[-1], points[0])

    return perimeter, num_holes

def plot_dxf(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.set_title("Aperçu DXF")

    for e in msp:
        if e.dxftype() == "LINE":
            start = e.dxf.start
            end = e.dxf.end
            ax.plot([start[0], end[0]], [start[1], end[1]], 'b-')
        elif e.dxftype() == "CIRCLE":
            center = e.dxf.center
            radius = e.dxf.radius
            circle = plt.Circle((center[0], center[1]), radius, color='r', fill=False)
            ax.add_patch(circle)
        elif e.dxftype() == "LWPOLYLINE":
            points = e.get_points("xy")
            x, y = zip(*points)
            ax.plot(x, y, 'g-')
            if e.closed:
                ax.plot([x[-1], x[0]], [y[-1], y[0]], 'g-')

    return fig

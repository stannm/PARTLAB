# 📄 Fichier : utils/dxf_reader.py

import ezdxf
import math
import matplotlib.pyplot as plt

def load_dxf(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        return doc
    except Exception as e:
        print("Erreur lors de la lecture du fichier DXF :", e)
        return None

def distance(p1, p2):
    return math.dist(p1, p2)

def arc_length(entity):
    start_angle = math.radians(entity.dxf.start_angle)
    end_angle = math.radians(entity.dxf.end_angle)
    angle = abs(end_angle - start_angle)
    return abs(angle * entity.dxf.radius)

def get_dxf_perimeter_and_holes(dxf_doc):
    msp = dxf_doc.modelspace()
    perimeter = 0.0
    num_holes = 0
    details = []

    for entity in msp:
        if entity.dxftype() == "LINE":
            length = distance(entity.dxf.start, entity.dxf.end)
            perimeter += length
            details.append(("Ligne", length))

        elif entity.dxftype() == "CIRCLE":
            length = 2 * math.pi * entity.dxf.radius
            perimeter += length
            num_holes += 1
            details.append(("Cercle", length))

        elif entity.dxftype() == "ARC":
            length = arc_length(entity)
            perimeter += length
            details.append(("Arc", length))

        elif entity.dxftype() == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) < 2:
                continue
            for i in range(len(points) - 1):
                perimeter += distance(points[i], points[i+1])
            if entity.closed:
                perimeter += distance(points[-1], points[0])
            details.append(("Polyligne", perimeter))

    return round(perimeter, 2), num_holes, details

def plot_dxf(dxf_doc):
    msp = dxf_doc.modelspace()
    fig, ax = plt.subplots()

    for entity in msp:
        if entity.dxftype() == "LINE":
            x = [entity.dxf.start[0], entity.dxf.end[0]]
            y = [entity.dxf.start[1], entity.dxf.end[1]]
            ax.plot(x, y, 'b')

        elif entity.dxftype() == "CIRCLE":
            circle = plt.Circle((entity.dxf.center[0], entity.dxf.center[1]), entity.dxf.radius,
                                color='r', fill=False)
            ax.add_patch(circle)

        elif entity.dxftype() == "ARC":
            arc = plt.Arc((entity.dxf.center[0], entity.dxf.center[1]),
                          2 * entity.dxf.radius, 2 * entity.dxf.radius,
                          angle=0,
                          theta1=entity.dxf.start_angle,
                          theta2=entity.dxf.end_angle,
                          color='orange')
            ax.add_patch(arc)

        elif entity.dxftype() == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) > 1:
                x, y = zip(*points)
                ax.plot(x, y, 'g')
                if entity.closed:
                    ax.plot([x[-1], x[0]], [y[-1], y[0]], 'g')

    ax.set_aspect('equal')
    plt.axis('off')
    plt.tight_layout()
    return fig

def modify_dxf(output_path, add_line=None, add_circle=None, add_rectangle=None):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    if add_line:
        start, end = add_line
        msp.add_line(start, end)

    if add_circle:
        center, radius = add_circle
        msp.add_circle(center=center, radius=radius)

    if add_rectangle:
        (x, y), width, height = add_rectangle
        msp.add_lwpolyline([
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)
        ], close=True)

    doc.saveas(output_path)
    return output_path

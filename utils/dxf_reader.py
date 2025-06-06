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
        t = entity.dxftype()

        if t == "LINE":
            length = distance(entity.dxf.start, entity.dxf.end)
            perimeter += length
            details.append(("Ligne", length))

        elif t == "CIRCLE":
            length = 2 * math.pi * entity.dxf.radius
            perimeter += length
            num_holes += 1
            details.append(("Cercle", length))

        elif t == "ARC":
            length = arc_length(entity)
            perimeter += length
            details.append(("Arc", length))

        elif t == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) < 2:
                continue
            for i in range(len(points) - 1):
                perimeter += distance(points[i], points[i + 1])
            if entity.closed:
                perimeter += distance(points[-1], points[0])
            details.append(("Polyligne", perimeter))

        elif t == "SPLINE":
            try:
                spline = entity.construction_tool()
                points = spline.approximate(segments=50)
                for i in range(len(points) - 1):
                    perimeter += distance(points[i], points[i + 1])
                details.append(("Spline", perimeter))
            except Exception as e:
                print("Erreur spline :", e)

        elif t == "POLYLINE":
            points = [v.dxf.location for v in entity.vertices()]
            if len(points) > 1:
                for i in range(len(points) - 1):
                    perimeter += distance(points[i], points[i + 1])
                if entity.is_closed:
                    perimeter += distance(points[-1], points[0])
                details.append(("Polyline (legacy)", perimeter))

    return round(perimeter, 2), num_holes, details


def plot_dxf(dxf_doc):
    msp = dxf_doc.modelspace()
    fig, ax = plt.subplots()

    for entity in msp:
        t = entity.dxftype()

        if t == "LINE":
            x = [entity.dxf.start[0], entity.dxf.end[0]]
            y = [entity.dxf.start[1], entity.dxf.end[1]]
            ax.plot(x, y, 'b')

        elif t == "CIRCLE":
            circle = plt.Circle((entity.dxf.center[0], entity.dxf.center[1]), entity.dxf.radius, color='r', fill=False)
            ax.add_patch(circle)

        elif t == "ARC":
            arc = plt.Arc((entity.dxf.center[0], entity.dxf.center[1]),
                          2 * entity.dxf.radius, 2 * entity.dxf.radius,
                          angle=0,
                          theta1=entity.dxf.start_angle,
                          theta2=entity.dxf.end_angle,
                          color='orange')
            ax.add_patch(arc)

        elif t == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) > 1:
                x, y = zip(*points)
                ax.plot(x, y, 'g')
                if entity.closed:
                    ax.plot([x[-1], x[0]], [y[-1], y[0]], 'g')

        elif t == "SPLINE":
            try:
                spline = entity.construction_tool()
                points = spline.approximate(segments=50)
                x, y = zip(*points)
                ax.plot(x, y, 'm')
            except Exception as e:
                print("Erreur d'affichage spline :", e)

        elif t == "POLYLINE":
            points = [v.dxf.location for v in entity.vertices()]
            if len(points) > 1:
                x, y = zip(*points)
                ax.plot(x, y, 'cyan')
                if entity.is_closed:
                    ax.plot([x[-1], x[0]], [y[-1], y[0]], 'cyan')

    ax.set_aspect('equal')
    plt.axis('off')
    plt.tight_layout()
    return fig

import ezdxf
import math
import matplotlib.pyplot as plt

def analyze_dxf_file(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
    except Exception as e:
        print("Erreur lors de la lecture du DXF :", e)
        return 0, 0, []

    perimeter = 0
    nb_holes = 0
    details = []

    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            length = math.dist(start, end)
            perimeter += length
            details.append(("LINE", length))

        elif entity.dxftype() == "LWPOLYLINE":
            points = entity.get_points('xy')
            closed = entity.closed
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                length = math.dist(p1, p2)
                perimeter += length
                details.append(("LWPOLYLINE", length))
            if closed:
                p1 = points[-1]
                p2 = points[0]
                length = math.dist(p1, p2)
                perimeter += length
                details.append(("LWPOLYLINE", length))

        elif entity.dxftype() == "CIRCLE":
            r = entity.dxf.radius
            length = 2 * math.pi * r
            perimeter += length
            nb_holes += 1
            details.append(("CIRCLE", length))

        elif entity.dxftype() == "ARC":
            start_angle = math.radians(entity.dxf.start_angle)
            end_angle = math.radians(entity.dxf.end_angle)
            angle = abs(end_angle - start_angle)
            arc_length = angle * entity.dxf.radius
            perimeter += arc_length
            details.append(("ARC", arc_length))

        elif entity.dxftype() == "SPLINE":
            try:
                fit_points = entity.fit_points
                for i in range(len(fit_points) - 1):
                    length = math.dist(fit_points[i], fit_points[i + 1])
                    perimeter += length
                    details.append(("SPLINE", length))
            except Exception:
                pass

    return round(perimeter, 2), nb_holes, details


def plot_dxf(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
    except Exception as e:
        print("Erreur lors de l'ouverture DXF :", e)
        return None

    fig, ax = plt.subplots()
    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            ax.plot([start[0], end[0]], [start[1], end[1]], 'b')

        elif entity.dxftype() == "LWPOLYLINE":
            points = entity.get_points('xy')
            x, y = zip(*points)
            ax.plot(x, y, 'g')
            if entity.closed:
                ax.plot([x[-1], x[0]], [y[-1], y[0]], 'g')

        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            r = entity.dxf.radius
            circle = plt.Circle((center[0], center[1]), r, color='r', fill=False)
            ax.add_patch(circle)

        elif entity.dxftype() == "ARC":
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            theta = [math.radians(a) for a in range(int(start_angle), int(end_angle))]
            x = [center[0] + radius * math.cos(t) for t in theta]
            y = [center[1] + radius * math.sin(t) for t in theta]
            ax.plot(x, y, 'orange')

    ax.set_aspect('equal')
    return fig

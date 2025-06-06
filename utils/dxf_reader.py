import ezdxf
import math
import matplotlib.pyplot as plt

def load_dxf(file_path):
    try:
        return ezdxf.readfile(file_path)
    except Exception as e:
        print("Erreur de chargement DXF :", e)
        return None

def distance(p1, p2):
    return math.dist(p1, p2)

def arc_length(arc):
    angle = abs(arc.dxf.end_angle - arc.dxf.start_angle)
    return math.radians(angle) * arc.dxf.radius

def get_dxf_perimeter_and_holes(doc):
    msp = doc.modelspace()
    perimeter = 0.0
    num_holes = 0
    details = []

    for e in msp:
        if e.dxftype() == "LINE":
            p1 = (e.dxf.start.x, e.dxf.start.y)
            p2 = (e.dxf.end.x, e.dxf.end.y)
            perimeter += distance(p1, p2)
            details.append(("LINE", p1, p2))

        elif e.dxftype() == "CIRCLE":
            r = e.dxf.radius
            perimeter += 2 * math.pi * r
            num_holes += 1
            details.append(("CIRCLE", (e.dxf.center.x, e.dxf.center.y), r))

        elif e.dxftype() == "ARC":
            length = arc_length(e)
            perimeter += length
            details.append(("ARC", e.dxf.center, e.dxf.radius))

        elif e.dxftype() in ("LWPOLYLINE", "POLYLINE"):
            points = e.get_points("xyb")
            for i in range(len(points) - 1):
                perimeter += distance(points[i][:2], points[i+1][:2])
            if e.is_closed:
                perimeter += distance(points[-1][:2], points[0][:2])
            details.append(("POLYLINE", points))

    return round(perimeter, 2), num_holes, details

def plot_dxf(doc):
    fig, ax = plt.subplots()
    msp = doc.modelspace()

    for e in msp:
        if e.dxftype() == "LINE":
            x1, y1 = e.dxf.start.x, e.dxf.start.y
            x2, y2 = e.dxf.end.x, e.dxf.end.y
            ax.plot([x1, x2], [y1, y2], color='cyan')

        elif e.dxftype() == "CIRCLE":
            cx, cy = e.dxf.center.x, e.dxf.center.y
            r = e.dxf.radius
            c = plt.Circle((cx, cy), r, color='orange', fill=False)
            ax.add_patch(c)

        elif e.dxftype() == "ARC":
            from matplotlib.patches import Arc
            arc = Arc(
                (e.dxf.center.x, e.dxf.center.y),
                width=2*e.dxf.radius,
                height=2*e.dxf.radius,
                angle=0,
                theta1=e.dxf.start_angle,
                theta2=e.dxf.end_angle,
                color='green'
            )
            ax.add_patch(arc)

        elif e.dxftype() in ("LWPOLYLINE", "POLYLINE"):
            points = e.get_points("xy")
            x, y = zip(*points)
            ax.plot(x, y, color='magenta')
            if e.is_closed:
                ax.plot([x[-1], x[0]], [y[-1], y[0]], color='magenta')

    ax.set_aspect('equal')
    ax.autoscale()
    ax.axis('off')
    return fig

def modify_dxf(file_path, **kwargs):
    if os.path.exists(file_path):
        doc = ezdxf.readfile(file_path)
    else:
        doc = ezdxf.new()
    msp = doc.modelspace()

    if 'add_line' in kwargs:
        p1, p2 = kwargs['add_line']
        msp.add_line(p1, p2)

    if 'add_circle' in kwargs:
        center, r = kwargs['add_circle']
        msp.add_circle(center=center, radius=r)

    if 'add_rectangle' in kwargs:
        (x, y), w, h = kwargs['add_rectangle']
        msp.add_lwpolyline([
            (x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)
        ], close=True)

    doc.saveas(file_path)

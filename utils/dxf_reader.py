import ezdxf
import math
import matplotlib.pyplot as plt

def load_dxf(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        return doc
    except Exception as e:
        print("Erreur de lecture DXF :", e)
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

    for e in msp:
        if e.dxftype() == 'LINE':
            start = e.dxf.start
            end = e.dxf.end
            d = distance(start[:2], end[:2])
            perimeter += d
            details.append(f"Ligne: {d:.2f} mm")

        elif e.dxftype() == 'CIRCLE':
            r = e.dxf.radius
            p = 2 * math.pi * r
            perimeter += p
            num_holes += 1
            details.append(f"Cercle: {p:.2f} mm")

        elif e.dxftype() == 'ARC':
            length = arc_length(e)
            perimeter += length
            details.append(f"Arc: {length:.2f} mm")

        elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            try:
                vertices = [tuple(v[:2]) for v in e.get_points()]
                for i in range(len(vertices) - 1):
                    perimeter += distance(vertices[i], vertices[i+1])
                if e.closed and len(vertices) > 1:
                    perimeter += distance(vertices[-1], vertices[0])
                details.append(f"Polyline: {perimeter:.2f} mm")
            except Exception as ex:
                print("Erreur LWPOLYLINE :", ex)

    return round(perimeter, 2), num_holes, details

def plot_dxf(dxf_doc):
    msp = dxf_doc.modelspace()
    fig, ax = plt.subplots()
    for e in msp:
        if e.dxftype() == 'LINE':
            x = [e.dxf.start[0], e.dxf.end[0]]
            y = [e.dxf.start[1], e.dxf.end[1]]
            ax.plot(x, y, color='blue')

        elif e.dxftype() == 'CIRCLE':
            circle = plt.Circle((e.dxf.center[0], e.dxf.center[1]), e.dxf.radius, fill=False, color='green')
            ax.add_patch(circle)

        elif e.dxftype() == 'ARC':
            start_angle = math.radians(e.dxf.start_angle)
            end_angle = math.radians(e.dxf.end_angle)
            angle_range = abs(end_angle - start_angle)
            arc = plt.Arc((e.dxf.center[0], e.dxf.center[1]), 2*e.dxf.radius, 2*e.dxf.radius, 
                          angle=0, theta1=e.dxf.start_angle, theta2=e.dxf.end_angle, color='orange')
            ax.add_patch(arc)

        elif e.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            try:
                vertices = [tuple(v[:2]) for v in e.get_points()]
                xs, ys = zip(*vertices)
                ax.plot(xs, ys, color='red')
            except Exception:
                continue

    ax.set_aspect('equal')
    ax.set_title("Aperçu DXF")
    return fig

def modify_dxf(output_path, **kwargs):
    doc = ezdxf.new()
    msp = doc.modelspace()

    if 'add_line' in kwargs:
        p1, p2 = kwargs['add_line']
        msp.add_line(p1, p2)

    if 'add_circle' in kwargs:
        center, radius = kwargs['add_circle']
        msp.add_circle(center, radius)

    if 'add_rectangle' in kwargs:
        (x, y), width, height = kwargs['add_rectangle']
        msp.add_lwpolyline([
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)
        ], close=True)

    doc.saveas(output_path)

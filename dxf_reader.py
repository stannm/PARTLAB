
import ezdxf
import math

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
        if entity.dxftype() == "LWPOLYLINE":
            points = entity.get_points()
            for i in range(len(points) - 1):
                perimeter += distance(points[i][0:2], points[i + 1][0:2])
            if entity.closed:
                perimeter += distance(points[-1][0:2], points[0][0:2])
            details.append(f"LWPOLYLINE – {len(points)} points")
        elif entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            perimeter += distance(start, end)
            details.append("LINE")
        elif entity.dxftype() == "ARC":
            perimeter += arc_length(entity)
            details.append("ARC")
        elif entity.dxftype() == "CIRCLE":
            perimeter += 2 * math.pi * entity.dxf.radius
            details.append("CIRCLE")
        elif entity.dxftype() == "SPLINE":
            try:
                spline = entity.construction_tool()
                approx_points = spline.approximate(50)
                for i in range(len(approx_points) - 1):
                    perimeter += distance(approx_points[i], approx_points[i + 1])
                details.append("SPLINE (approx. 50 seg)")
            except:
                details.append("SPLINE (non analysée)")

    return round(perimeter, 2), num_holes, details

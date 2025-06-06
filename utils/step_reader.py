import ezdxf
import math

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

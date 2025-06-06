import cadquery as cq
import numpy as np

def read_step_file(file_path):
    try:
        part = cq.importers.importStep(file_path)
        return part
    except Exception:
        return None

def get_perimeter_and_features(part):
    try:
        shapes = part.val().Faces()
        perimeter = 0
        num_holes = 0
        is_bent = False

        for face in shapes:
            wires = face.Wires()
            if wires:
                lengths = [w.Length() for w in wires]
                if lengths:
                    perimeter += lengths[0]
                    if len(lengths) > 1:
                        num_holes += len(lengths) - 1

        bb = part.val().BoundingBox()
        height = bb.zmax - bb.zmin
        is_bent = height > 2.0

        return round(perimeter, 2), num_holes, is_bent

    except Exception:
        return 0, 0, False

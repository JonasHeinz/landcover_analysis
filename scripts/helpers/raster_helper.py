from shapely.geometry import box 

def calculate_vectorbox(point, boxsize):
    x, y = point.x, point.y
    return box(x - boxsize/2, y - boxsize/2, x + boxsize/2, y + boxsize/2)

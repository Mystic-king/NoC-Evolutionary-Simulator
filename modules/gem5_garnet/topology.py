def mesh_neighbors(node,rows,cols):
    r,c=node
    return [(nr,nc) for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=nr<rows and 0<=nc<cols]

def xy_route(source,destination):
    """Deterministic dimension-order XY route: move horizontally, then vertically."""
    r,c=source; tr,tc=destination; path=[(r,c)]
    while c!=tc: c += 1 if tc>c else -1; path.append((r,c))
    while r!=tr: r += 1 if tr>r else -1; path.append((r,c))
    return path

def validate_mesh(rows,cols):
    if not 2<=rows<=32 or not 2<=cols<=32: raise ValueError("Mesh rows and columns must be between 2 and 32.")

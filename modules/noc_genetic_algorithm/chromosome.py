"""Path representation helpers for mesh routing chromosomes."""
def path_to_moves(path):
    moves=[]
    for (r1,c1),(r2,c2) in zip(path,path[1:]):
        moves.append("E" if c2>c1 else "W" if c2<c1 else "S" if r2>r1 else "N")
    return moves

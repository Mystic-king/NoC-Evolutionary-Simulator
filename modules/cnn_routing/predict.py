def predict_next_hop(model_path,source,destination,congestion=None):
    """Load a trained checkpoint and predict the XY next-hop direction."""
    import numpy as np, torch
    from modules.cnn_routing.model import build_model
    checkpoint=torch.load(model_path,map_location="cpu",weights_only=False)
    size=int(checkpoint["grid_size"])
    for node in (source,destination):
        if len(node)!=2 or not (0<=node[0]<size and 0<=node[1]<size):
            raise ValueError(f"Router coordinate {node} is outside the {size}x{size} mesh.")
    if tuple(source)==tuple(destination):
        raise ValueError("Source and destination must differ.")
    model=build_model(size); model.load_state_dict(checkpoint["state_dict"]); model.eval()
    x=np.zeros((1,3,size,size),dtype=np.float32)
    x[0,0,source[0],source[1]]=1; x[0,1,destination[0],destination[1]]=1
    if congestion is not None: x[0,2]=np.asarray(congestion,dtype=np.float32)
    with torch.no_grad(): ix=int(model(torch.from_numpy(x)).argmax(1).item())
    return checkpoint["classes"][ix]

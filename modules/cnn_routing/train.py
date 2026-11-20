from pathlib import Path
import random
import numpy as np

def run_cnn_demo(samples=1600,epochs=8,batch_size=64,learning_rate=.001,grid_size=8,seed=42,output_dir="models"):
    try:
        import torch
        from torch import nn
        from torch.utils.data import TensorDataset,DataLoader
    except ImportError as exc:
        raise RuntimeError("CNN experiment requires PyTorch. Install with: pip install -e '.[ml]'") from exc
    from modules.cnn_routing.dataset import generate_routing_dataset
    from modules.cnn_routing.model import build_model
    if samples<100 or epochs<1 or batch_size<4: raise ValueError("Use samples >= 100, epochs >= 1 and batch_size >= 4.")
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    x,y=generate_routing_dataset(samples,grid_size,seed)
    perm=np.random.default_rng(seed).permutation(samples); split=int(samples*.8)
    tr,va=perm[:split],perm[split:]
    train=TensorDataset(torch.from_numpy(x[tr]),torch.from_numpy(y[tr]))
    valid_x=torch.from_numpy(x[va]); valid_y=torch.from_numpy(y[va])
    loader=DataLoader(train,batch_size=batch_size,shuffle=True,generator=torch.Generator().manual_seed(seed))
    model=build_model(grid_size); optimizer=torch.optim.Adam(model.parameters(),lr=learning_rate); loss_fn=nn.CrossEntropyLoss()
    history=[]
    for epoch in range(epochs):
        model.train(); total=0
        for xb,yb in loader:
            optimizer.zero_grad(); logits=model(xb); loss=loss_fn(logits,yb); loss.backward(); optimizer.step()
            total+=float(loss.item())*len(xb)
        model.eval()
        with torch.no_grad():
            logits=model(valid_x); val_loss=float(loss_fn(logits,valid_y).item())
            accuracy=float((logits.argmax(1)==valid_y).float().mean().item())
        history.append({"epoch":epoch+1,"train_loss":total/len(train),"validation_loss":val_loss,"validation_accuracy":accuracy})
    model.eval()
    with torch.no_grad():
        pred=model(valid_x).argmax(1).cpu().numpy()
    class_names=["EAST","WEST","SOUTH","NORTH"]
    confusion=np.zeros((4,4),dtype=int)
    for a,b in zip(y[va],pred): confusion[int(a),int(b)]+=1
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    model_path=out/"cnn_routing_model.pt"; torch.save({"state_dict":model.state_dict(),"grid_size":grid_size,"classes":class_names,"seed":seed},model_path)
    prediction_rows=[{"sample_index":int(i),"actual":class_names[int(a)],"predicted":class_names[int(b)],
                       "correct":bool(a==b)} for i,a,b in zip(va,y[va],pred)]
    return {"model":"CNN routing direction classifier","dataset_samples":samples,"training_samples":len(tr),
            "validation_samples":len(va),"grid_size":grid_size,"epochs":epochs,
            "validation_accuracy":history[-1]["validation_accuracy"],"validation_loss":history[-1]["validation_loss"],
            "classes":class_names,"confusion_matrix":confusion.tolist(),"model_path":str(model_path),
            "history":history,"predictions":prediction_rows}

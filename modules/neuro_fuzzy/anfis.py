"""Compact two-input, four-rule Sugeno ANFIS with hybrid learning."""
import numpy as np
from modules.neuro_fuzzy.membership import gaussian_membership
from modules.neuro_fuzzy.fuzzy_rules import rule_descriptions

def _design(x,y,centers,sigmas):
    mx=np.column_stack([gaussian_membership(x,centers[0,j],sigmas[0,j]) for j in range(2)])
    my=np.column_stack([gaussian_membership(y,centers[1,j],sigmas[1,j]) for j in range(2)])
    firing=np.column_stack([mx[:,0]*my[:,0],mx[:,0]*my[:,1],mx[:,1]*my[:,0],mx[:,1]*my[:,1]])
    norm=firing/(firing.sum(axis=1,keepdims=True)+1e-12)
    blocks=[norm[:,i,None]*np.column_stack([x,y,np.ones_like(x)]) for i in range(4)]
    return np.concatenate(blocks,axis=1),norm

def _fit_predict(x,y,target,centers,sigmas):
    design,_=_design(x,y,centers,sigmas)
    coeff=np.linalg.lstsq(design,target,rcond=None)[0]
    return design@coeff,coeff

def run_anfis_demo(samples=350,epochs=25,learning_rate=.035,seed=42):
    if samples<50: raise ValueError("samples must be >= 50")
    if epochs<1: raise ValueError("epochs must be >= 1")
    if learning_rate<=0: raise ValueError("learning_rate must be positive")
    rng=np.random.default_rng(seed)
    x=rng.uniform(-1,1,samples); y=rng.uniform(-1,1,samples)
    target=np.sin(np.pi*x)*np.cos(np.pi*y)
    order=rng.permutation(samples); split=int(samples*.8); tr,va=order[:split],order[split:]
    centers=np.array([[-.5,.5],[-.5,.5]],dtype=float)
    sigmas=np.full((2,2),.65,dtype=float)
    history=[]
    # Hybrid ANFIS: least-squares consequent update + finite-difference premise update.
    def loss_for(c,s):
        pred,_=_fit_predict(x[tr],y[tr],target[tr],c,s)
        return float(np.mean((pred-target[tr])**2))
    eps=1e-3
    for epoch in range(epochs):
        base=loss_for(centers,sigmas)
        grad_c=np.zeros_like(centers); grad_s=np.zeros_like(sigmas)
        for idx in np.ndindex(centers.shape):
            cp=centers.copy(); cm=centers.copy(); cp[idx]+=eps; cm[idx]-=eps
            grad_c[idx]=(loss_for(cp,sigmas)-loss_for(cm,sigmas))/(2*eps)
            sp=sigmas.copy(); sm=sigmas.copy(); sp[idx]+=eps; sm[idx]=max(.08,sm[idx]-eps)
            grad_s[idx]=(loss_for(centers,sp)-loss_for(centers,sm))/(2*eps)
        centers=np.clip(centers-learning_rate*grad_c,-1.5,1.5)
        sigmas=np.clip(sigmas-learning_rate*grad_s,.08,2.0)
        pred,_=_fit_predict(x[tr],y[tr],target[tr],centers,sigmas)
        val_pred,_=_fit_predict(x[tr],y[tr],target[tr],centers,sigmas)
        # Evaluate validation with the same trained consequent parameters.
        design_tr,_=_design(x[tr],y[tr],centers,sigmas); coeff=np.linalg.lstsq(design_tr,target[tr],rcond=None)[0]
        design_va,_=_design(x[va],y[va],centers,sigmas)
        val_mse=float(np.mean((design_va@coeff-target[va])**2))
        history.append({"epoch":epoch+1,"train_mse":float(np.mean((pred-target[tr])**2)),"validation_mse":val_mse})
    design_tr,_=_design(x[tr],y[tr],centers,sigmas); coeff=np.linalg.lstsq(design_tr,target[tr],rcond=None)[0]
    design_va,_=_design(x[va],y[va],centers,sigmas); predictions=design_va@coeff
    rmse=float(np.sqrt(np.mean((predictions-target[va])**2)))
    rows=[{"x":float(a),"y":float(b),"actual":float(t),"predicted":float(q),"absolute_error":float(abs(t-q))}
          for a,b,t,q in zip(x[va],y[va],target[va],predictions)]
    return {"model":"Two-input four-rule Sugeno ANFIS","target_function":"sin(pi*x) * cos(pi*y)",
            "train_samples":len(tr),"validation_samples":len(va),"validation_rmse":rmse,
            "rules":rule_descriptions(),"membership_centers":centers.tolist(),
            "membership_sigmas":sigmas.tolist(),"consequent_coefficients":coeff.tolist(),
            "history":history,"predictions":rows}

import numpy as np

def gaussian_membership(x,center,sigma):
    sigma=max(float(sigma),1e-4)
    return np.exp(-0.5*((np.asarray(x)-center)/sigma)**2)

def build_model(grid_size=8):
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("CNN experiment requires PyTorch. Install with: pip install -e '.[ml]'") from exc
    class RoutingCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features=nn.Sequential(
                nn.Conv2d(3,16,kernel_size=3,padding=1),nn.ReLU(),
                nn.Conv2d(16,32,kernel_size=3,padding=1),nn.ReLU(),
                nn.MaxPool2d(2),nn.Conv2d(32,32,kernel_size=3,padding=1),nn.ReLU(),
                nn.AdaptiveAvgPool2d((2,2)),nn.Flatten(),
            )
            self.classifier=nn.Sequential(nn.Linear(32*2*2,64),nn.ReLU(),nn.Dropout(.15),nn.Linear(64,4))
        def forward(self,x): return self.classifier(self.features(x))
    return RoutingCNN()

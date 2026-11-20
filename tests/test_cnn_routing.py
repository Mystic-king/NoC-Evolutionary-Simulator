import pytest

def test_cnn_dataset_shapes_and_labels():
    np=pytest.importorskip("numpy")
    from modules.cnn_routing.dataset import generate_routing_dataset
    x,y=generate_routing_dataset(samples=50,grid_size=5,seed=1)
    assert x.shape==(50,3,5,5)
    assert y.shape==(50,)
    assert set(y.tolist()).issubset({0,1,2,3})

def test_cnn_training_smoke(tmp_path):
    pytest.importorskip("torch")
    from modules.cnn_routing.train import run_cnn_demo
    r=run_cnn_demo(samples=100,epochs=1,batch_size=16,grid_size=4,seed=2,output_dir=tmp_path)
    assert 0<=r["validation_accuracy"]<=1
    assert (tmp_path/"cnn_routing_model.pt").exists()
    from modules.cnn_routing.predict import predict_next_hop
    direction=predict_next_hop(tmp_path/"cnn_routing_model.pt",(0,0),(3,3))
    assert direction in {"EAST","WEST","SOUTH","NORTH"}

import json

from time import time
timer = time()
from .Model.dataset import BaseDataset, AggDataset
from .Model.model import Resnet, CNN2D
from .Model.predict import PipelinePredict

def pipeline(inp_path = 'dir_path',
             pth_path = 'pth_path',
             model_type = None,
             out_path = 'dir_path',
             isAgg = True):
    
    # init dataset
    timer = time()
    
    if isAgg:
        dataset = AggDataset(dir_path=inp_path)
    else:
        dataset = BaseDataset(dir_path=inp_path)
    
    # model architecture
    if not model_type:
        print("No model type specified!")
        return
    elif model_type == 'CNN2D':
        model = CNN2D()
    elif model_type == 'Resnet':
        model = Resnet(num_residual_block=[3,4,6,3])
    
    # init pipeline
    pipeline = PipelinePredict(model_architecture=model,
                              model_path=pth_path)
    
    # predict 
    print("Predicting...")
    pipeline.predict(dataset)
    
    # export_result
    dataset.export_result(out_path)
    print("Completed!")
    print(f'Time executed: {time() - timer:.2f}s')
    
if __name__ == '__main__':
    json_path = '/N/slate/tnn3/DucHGA/PipelineTC/Src/Model/config.json'
    var = json.load(open(json_path, "r"))
    print(f'Time prepared: {time() - timer:.2f}s')
    pipeline(inp_path = var['inp_path'],
             out_path = var['out_path'],
             model_type = var['model_type'],
             pth_path = var['pth_path'],
             isAgg = var['isAgg'])
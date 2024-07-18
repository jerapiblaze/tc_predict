import torch
import os

import numpy as np

from .model import Resnet, CNN2D

from torch.utils.data import DataLoader

class PipelinePredict():
    def __init__(self,
                 model_architecture = CNN2D(),
                 model_path = 'path',
                 batch_size = 1,
                 num_workers = os.cpu_count(),
                 pin_memory = True if torch.cuda.is_available() else False,
                 device = 'cuda' if torch.cuda.is_available() else 'cpu'):
        
        self.device = device
        self.model = model_architecture.to(self.device)
        self.model.load_state_dict(torch.load(model_path)['model_state_dict'], strict=False)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        self.batch_size = batch_size
        self.pin_memory = pin_memory
        self.num_workers = num_workers
        self.dataLoader = 'hihi'
    
    def predict(self, input_DS):
        # init DataLoader from input Dataset
        self.dataLoader = DataLoader(input_DS,
                                     batch_size=self.batch_size,
                                     pin_memory=self.pin_memory,
                                     num_workers=self.num_workers,
                                     shuffle=False)
        self.model.eval()
        score_list = []
        for batch_input in self.dataLoader:
            batch_input = batch_input.to(self.device)
            
            # predict
            pred = self.model(batch_input)
            score_list.extend(pred.cpu().detach().numpy())
        
        score_list = np.array(score_list)
        input_DS.assign_predict(score_list)
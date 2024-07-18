import os
import torch

import pandas as pd
import numpy as np
import xarray as xr

from torch.utils.data import Dataset

SINGLE_VAR = ['tmpsfc', 'pressfc', 'landmask', 'hgttrp', 'tmptrp']
PRESS_VAR = ['ugrdprs', 'vgrdprs', 'vvelprs', 'tmpprs', 'hgtprs', 'rhprs']
LEVEL = 21

#################
# General Dataset
#################

class NcepDataset(Dataset):
    def __init__(self,
                 dir_path):
        
        self.dir_path = dir_path
        self.df = pd.DataFrame(columns=['datetime', 'lat', 'lon', 'sample_path', 'label', 'score'])
    
    def __len__(self):
        print(self.df.shape[0], 'samples in Dataset!')
        return self.df.shape[0]
    
    def assign_predict(self,
                       score_list = [],):
        
        self.df['score'] = score_list
        self.df['label'] = (score_list > 0.5).astype(int)
    
    def export_result(self,
                      out_path = 'dir_path'):
        self.df.to_csv(os.path.join(out_path, 'output.csv'), index=None)

#################
# Non-agg Dataset
#################
class BaseDataset(NcepDataset):
    def __init__(self,
                 dir_path: str,):
        NcepDataset.__init__(self, dir_path)
    
        # generate list of sample
        list_sample = [path 
                       for path in os.listdir(self.dir_path) 
                       if os.path.isdir(os.path.join(self.dir_path, path))]
        list_sample.sort()
        self.df['sample_path'] = list_sample
    
    def __getitem__(self, index):
        sample_path = os.path.join(self.dir_path,
                                   self.df.loc[index, 'sample_path'])
        
        alpha = 0.85
        agg_ft = np.zeros((131, 17, 17), dtype=np.float32)
        
        for step in range(5):
            step_path = os.path.join(sample_path,
                                     f'{step}.nc')
            
            if os.path.exists(step_path):
                # read data
                ds = xr.open_dataset(step_path)
                step_ft = []
                
                for var in SINGLE_VAR:
                    arr = ds.variables[var].data[0]           
                    step_ft.append(arr)
                    
                for var in PRESS_VAR:
                    arr = ds.variables[var].data[0][: LEVEL]
                    step_ft.extend(arr)
                    
                # normalize ...
                
                # aggregate
                agg_ft = agg_ft + np.multiply(step_ft, alpha ** step)
                
        agg_ft = torch.tensor(np.array(agg_ft), dtype=torch.float)
        return agg_ft
        
#############
# Agg Dataset
#############
class AggDataset(NcepDataset):
    def __init__(self,
                 dir_path: str,):
        NcepDataset.__init__(self, dir_path)
        # generate list of sample
        list_sample = [file 
                       for file in os.listdir(self.dir_path) 
                       if os.path.isfile(os.path.join(self.dir_path, file))]
        list_sample.sort()
        self.df['sample_path'] = list_sample
    
    def __getitem__(self, index):
        sample_path = os.path.join(self.dir_path,
                                   self.df.loc[index, 'sample_path'])
        
        ds = xr.open_dataset(sample_path)
        ft = []
        
        for var in SINGLE_VAR:
            arr = ds.variables[var].data[0]           
            ft.append(arr)
            
        for var in PRESS_VAR:
            arr = ds.variables[var].data[0][: LEVEL]
            ft.extend(arr)
            
        # normalize ...
        ft = torch.tensor(np.array(ft), dtype=torch.float)
        return ft
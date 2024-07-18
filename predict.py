# READ INPUTS (*.nc)

# CREATE TEMP FILES (*.nc)

# RUN PREDICT ENGINE (return *.csv)

# CONVERT CSV -> DATA ARRAY

# PLOT

import logging
import os
os.environ["PREDICT_LOG_LEVEL"] = f"{logging.INFO}"
logging.basicConfig(format='%(asctime)s %(name)s pid=%(process)-7d | %(levelname)-8s | %(message)s', level=int(os.environ["PREDICT_LOG_LEVEL"]))
logger = logging.getLogger(
    name=__name__
)

import xarray as xr
import shutil
import datetime
import libctg_WeatherDataset as wd
from libtcg_SliceWindow import SliceWindow
from libtcg_PredictEngines.PipelineTC.pipeline import pipeline as Predictor
from utilities.csv2nc import PipelineTC_csv2nc as CSV2NCconverter
from utilities.plot import Plot

FNL = wd.NcepFnl()
MERRA2 = wd.NasaMerra2()

def Predict(
    input_path:str, output_path:str='./data/output',
    model_type:str='CNN2D', model_path:str='./data/models/model.pt',
    proc_count:int=8, subproc_count:int=128,
    clean_up:bool=False,
    plot_fig:bool=True
) -> xr.Dataset:
    # DUMMY FOR TESTING
    prediction_time = datetime.datetime.now()
    output_path = os.path.join('data', 'output')
    temp_path = os.path.join('data', 'temp', f'{prediction_time.strftime("%Y%m%d_%H%M%S")}')
    
    logger.info("Predict parameters")
    logger.info(f"input_dir  = {input_path}")
    logger.info(f"temp_dir   = {temp_path}")
    logger.info(f"output_dir = {output_path}")
    logger.info(f"model_type = {model_type}")
    logger.info(f"model_path = {model_path}")
    
    os.mkdir(temp_path)
    
    # SLICE WINDOW
    logger.info("Create slice windows")
    slice_windows_path = os.path.join(temp_path, "slice_windows")
    os.mkdir(slice_windows_path)
    SliceWindow(
        FNL, input_path, slice_windows_path,
        lat_min=0,
        lat_max=30,
        lon_min=100,
        lon_max=150,
        proc_count=proc_count,
        subproc_count=subproc_count
    )
    
    # PREDICT
    logger.info("Predict")
    prediction_path = os.path.join(temp_path, "prediction_result")
    os.mkdir(prediction_path)
    Predictor(
        inp_path=slice_windows_path,
        pth_path=model_path,
        model_type=model_type,
        out_path=prediction_path,
        isAgg=False
    )
    
    # CONVERT CSV TO DATASET
    logger.info("Convert")
    predict_file = os.path.join(prediction_path, "output.csv")
    
    output_file_path = os.path.join(output_path, f"{prediction_time.strftime('%Y%m%d_%H%M%S')}.nc")
    result_ds = CSV2NCconverter(
        predict_file=predict_file,
        output_file_path=output_file_path
    )
    
    if plot_fig:
        output_plot_path = os.path.join(output_path, f"{prediction_time.strftime('%Y%m%d_%H%M%S')}.pdf")
        Plot(result_ds, output_plot_path)
    
    # CLEAN UP
    if clean_up:
        shutil.rmtree(temp_path)
    
    # END
    finish_time = datetime.datetime.now()
    diff = finish_time - prediction_time
    
    logger.info(f"total_time: {diff}")
    exit()

if __name__=="__main__":
    Predict(
        input_path='data/input/sample4'
    )
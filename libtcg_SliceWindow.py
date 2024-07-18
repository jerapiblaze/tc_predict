import os
import logging
logging.basicConfig(format='%(asctime)s %(name)s pid=%(process)-7d | %(levelname)-8s | %(message)s', level=int(os.environ["PREDICT_LOG_LEVEL"]))
logger = logging.getLogger(
    name=__name__
)

import datetime
import numpy as np
import multiprocessing as mp
from libctg_WeatherDataset import WeatherDataset, FindNearest
from utilities.dir import RecurseListDir
from utilities.datetime import convert_datetime64_to_datetime

def SliceWindow(
    WD: WeatherDataset, input_path:str, output_path:str,
    lat_min:float = None, lat_max:float=None, lon_min:float=None, lon_max:float=None,
    lat_dim:float=17, lon_dim:float=17,
    nstep:int=1,
    proc_count:int=1,
    subproc_count:int=1
):
    queue = mp.Queue()
    input_file_paths = RecurseListDir(input_path, ["*.nc"])
    logger.info(f"Total input files: {len(input_file_paths)}")
    for input_file_path in input_file_paths:
        queue.put((
            input_file_path, output_path,
            lat_min, lat_max, lon_min, lon_max,
            lat_dim, lon_dim,
            nstep
        ))
        
    for i in range(proc_count):
        queue.put(None)
    
    proc = []
    for i in range(proc_count):
        p = mp.Process(
            target=GetSliceWindow_Worker,
            args=(queue, WD, subproc_count)
        )
        p.start()
        proc.append(p)
    for p in proc:
        p.join()
    
        
def GetSliceWindow_Worker(queue:mp.Queue, WD: WeatherDataset, subproc_count:int):
    child_logger = logger.getChild("GetSliceWindows_Worker")
    child_logger.info(f"Start")
    while (queue.qsize()):
        try:
            job = queue.get(timeout=5)
        except:
            continue
        if not (type(job) is tuple):
            break
        child_logger.debug(f"Remaining queue size: {queue.qsize()}")
        input_file_path, output_path, lat_min, lat_max, lon_min, lon_max, lat_dim, lon_dim, nstep = job
        GetSliceWindow(
            WD, input_file_path, output_path,
            lat_min, lat_max, lon_min, lon_max,
            lat_dim, lon_dim,
            nstep,
            proc_count=subproc_count
        )
    child_logger.info(f"Exit!")
    exit()

def GetSliceWindow(
    WD: WeatherDataset, wd_path:str, output_path:str, 
    lat_min:float=None, lat_max:float=None, lon_min:float=None, lon_max:float=None,
    lat_dim:float=17, lon_dim:float=17,
    nstep:int=1,
    proc_count:int=1
):
    w_ds = WD.LoadFromDisk(wd_path)
    LAT_ARR = np.asarray(w_ds["latitude"].values)
    LON_ARR = np.asarray(w_ds["longitude"].values)
    # print(LAT_ARR)
    # print(LON_ARR)
    lat_min = np.min(LAT_ARR) if lat_min is None else FindNearest(LAT_ARR, lat_min)
    lat_max = np.max(LAT_ARR) if lat_max is None else FindNearest(LAT_ARR, lat_max)
    lon_min = np.min(LON_ARR) if lon_min is None else FindNearest(LON_ARR, lon_min)
    lon_max = np.max(LON_ARR) if lon_max is None else FindNearest(LON_ARR, lon_max)
    # print(lat_min, lat_max, lon_min, lon_max)
    # lat_min = FindNearest(w_ds["latitude"].values, configs.SequenceArea.MIN_LAT)
    # lat_max = FindNearest(w_ds["latitude"].values, configs.SequenceArea.MAX_LAT)
    # lon_min = FindNearest(w_ds["longitude"].values, configs.SequenceArea.MIN_LON)
    # lon_max = FindNearest(w_ds["longitude"].values, configs.SequenceArea.MAX_LON)
    # Find first area center point at top left
    lat_c = lat_min + int(WD.DIM_LAT/2)*(WD.STEP_LAT)
    lon_c = lon_max - int(WD.DIM_LON/2)*(WD.STEP_LON)
    # Calculate max value of lat at center point
    lat_c_max = lat_max - int(WD.DIM_LAT/2)*(WD.STEP_LAT)
    # Calculate min value of lon at center point
    lon_c_min = lon_min + int(WD.DIM_LON/2)*(WD.STEP_LON)

    # # Get date and time from file path
    # # example path: "./data/temp/ncep-fnl/fnl_20070725_12_00.grib1.nc"
    # filename = wd_path.split("/")[4].split(".")[0] # fnl_20070725_12_00
    # tmp_date = filename.split("_")[1] 
    # tmp_hour = filename.split("_")[2]
    # tmp_minute = filename.split("_")[3]
    # tmp_year = tmp_date[0:4]
    # tmp_month = tmp_date[4:6]
    # tmp_day = tmp_date[6:8]

    # if int(tmp_year) < configs.SequenceArea.MIN_YEAR:
    #     return

    # Get date and time from file name
    # date_time = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day), int(tmp_hour), int(tmp_minute))
    # date_time = datetime.datetime.strptime(w_ds.attrs["ISO_TIME"], "%Y-%m-%d %H:%M:%S")
    # date_time = datetime.datetime.fromtimestamp(w_ds["time"].values[0].astype(datetime.datetime))
    # date_time = w_ds["time"].values[0].astype(datetime.datetime)
    date_time = convert_datetime64_to_datetime(w_ds["time"].values[0])
    # print(date_time)
    date_c = date_time.date()
    time_c = date_time.time()

    # Resolve the symlink to get the actual target path
    real_path = os.path.realpath(output_path)

    # Create sub folder
    # sub_path = os.path.join(real_path, filename)
    # os.mkdir(sub_path)

    # if os.access(real_path, os.W_OK):  # Check write permission
    #     # Create the subdirectory if permission granted
    #     os.mkdir(sub_path)
    # else:
    #     print(f"Error: Permission denied to create directory in {real_path}")
    #     return
    
    # if not os.access(sub_path, os.W_OK):  # Check write permission
    #     print(f"Error: Permission denied to create directory in {sub_path}")
    #     return

    """
    SAVE PATH: {temp}/{lat}_{lon}/{time}.nc
    """

    # # Move center point from left to right, top to bottom
    # lat_start = lat_c
    # while lat_start <= lat_c_max:
    #     lon_index = lon_c  # Reset lon_index for each latitude
    #     while lon_index >= lon_c_min:
    #         print(f"{lat_start}_{lon_index}")
    #         s_ds = WD.GetSample(w_ds, "", lat_start, lon_index, date_c, time_c, negative_type="SEQUENCE_AREA")
    #         if not s_ds:
    #             print("not s_ds")
    #             lon_index -= nstep * WD.STEP_LON
    #             continue
            
    #         sample_path = os.path.join(real_path, f"{lat_start}_{lon_index}")            
    #         if not os.path.exists(sample_path):
    #             os.mkdir(sample_path)

    #         save_path = os.path.join(sample_path, f"{date_time.strftime('%Y%m%d_%H%M')}.nc")
    #         WD.SaveToDisk(save_path, s_ds)
    #         lon_index -= nstep * WD.STEP_LON

    #     lat_start += nstep * WD.STEP_LAT # Move to the next latitude
    
    # for i in range(len(LAT_ARR)):
    #     for j in range(len(LON_ARR)):
    #         if not nstep == 1:
    #             if i%nstep or j%nstep:
    #                 continue
    #         lat_c = LAT_ARR[i]
    #         lon_c = LON_ARR[j]
    #         if lat_c > lat_max or lon_c > lon_max or lat_c < lat_min or lon_c < lon_min:
    #             continue
    #         s_ds = WD.GetSample(w_ds, "", lat_c, lon_c, date_c, time_c, lat_dim, lon_dim, negative_type="SEQUENCE_AREA")
    #         if not s_ds:
    #             continue
    #         sample_path = os.path.join(real_path, f"{lat_c}_{lon_c}")            
    #         if not os.path.exists(sample_path):
    #             os.mkdir(sample_path)

    #         save_path = os.path.join(sample_path, f"{date_time.strftime('%Y%m%d_%H%M')}.nc")
    #         WD.SaveToDisk(save_path, s_ds)
            
    queue = mp.Queue()

    for i in range(len(LAT_ARR)):
        for j in range(len(LON_ARR)):
            if not nstep == 1:
                if i%nstep or j%nstep:
                    continue
            lat_c = LAT_ARR[i]
            lon_c = LON_ARR[j]
            if lat_c > lat_max or lon_c > lon_max or lat_c < lat_min or lon_c < lon_min:
                continue
            sample_path = os.path.join(real_path, f"{lat_c}_{lon_c}")            
            if not os.path.isdir(sample_path):
                try:
                    os.mkdir(sample_path)
                except FileExistsError:
                    pass
            save_path = os.path.join(sample_path, f"{date_time.strftime('%Y%m%d_%H%M')}.nc")
            queue.put((lat_c, lon_c, date_c, time_c, lat_dim, lon_dim, save_path))
            
    for i in range(proc_count):
        queue.put(None)
    
    proc = []
    for i in range(proc_count):
        p = mp.Process(
            target=GetSample_Worker,
            args=(queue, WD, w_ds)
        )
        p.start()
        proc.append(p)
    for p in proc:
        p.join()
            
def GetSample_Worker(queue:mp.Queue, WD:WeatherDataset, w_ds):
    child_logger = logger.getChild(f"GetSample_Worker@{os.getppid()}")
    child_logger.info("Start!")
    while (queue.qsize()):
        try:
            job = queue.get(timeout=5)
        except:
            continue
        if not (type(job) is tuple):
            break
        child_logger.debug(f"Remaining queue size: {queue.qsize()}")
        lat_c, lon_c, date_c, time_c, lat_dim, lon_dim, save_path = job
        s_ds = WD.GetSample(w_ds, "", lat_c, lon_c, date_c, time_c, lat_dim, lon_dim, negative_type="SEQUENCE_AREA")
        if not s_ds:
            continue
        WD.SaveToDisk(save_path, s_ds)
    child_logger.info("Exit!")
    exit()
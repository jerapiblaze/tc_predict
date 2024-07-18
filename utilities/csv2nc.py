import os
import xarray as xr
import pandas as pd

def PipelineTC_csv2nc(predict_file:str, output_file_path:str) -> xr.Dataset:
    result_df = pd.read_csv(
        filepath_or_buffer=predict_file,
        delimiter=",",
        usecols=["lat","lon","sample_path", "score"]
    )
    for ind in result_df.index:
        samplepath = result_df['sample_path'][ind]
        la, lo = (float(i) for i in str(samplepath).split("_"))
        sco = float(result_df['score'][ind])
        result_df.at[ind, 'score'] = sco
        result_df.at[ind, 'lat'] = la
        result_df.at[ind, 'lon'] = lo
        
    result_df.drop(columns=["sample_path"], inplace=True)
    
    result_df.set_index(['lat', 'lon'], inplace=True)

    
    result_ds = xr.Dataset.from_dataframe(result_df)
    
    result_ds.to_netcdf(output_file_path)
    
    return result_ds
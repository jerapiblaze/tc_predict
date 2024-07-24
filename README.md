# TC_PREDICT PIPELINE


### Prerequisites
* Typhoon prediction engines: [PipelineTC](https://github.com/AnhDucHoangGia/PipelineTC/)
* Datasets: * `ncep-fnl` or * `nasa-merra2` (in `*.nc` format)

### Input

* Input folder: `./data/input`
* Input files: NetCDF (`*.nc`, `*.nc4`) files containing weather data at ONE timestamp.

### Output

* One NetCDF file (`*.nc`) containing the prediction result for the considering sample (continuous value ranging in `[0,1]`)
* One rendered plot from prediction result (`*.pdf`).

![Demo rendered result](demo.png "Demo rendered result")

### Parameters

Work.In.Progress...

### Usage (interactive)

Typical: `python predict.py ./data/input/predict`

For more complex usages, see `python predict.py -h`

```console
$ python predict.py -h
usage: predict.py [-h] [-o OUTPUT] [-d] [-m MODEL_TYPE] [-p MODEL_PATH] [-n] [-i CONCURRENT_PROCESS_COUNT] [-t CONCURRENT_THREAD_COUNT] input

positional arguments:
  input                 Input folder. Example: './data/input/sample4'

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output folder. Example: './data/output'
  -d, --delete-temp-files
                        Delete temporary data files.
  -m MODEL_TYPE, --model-type MODEL_TYPE
                        Model name
  -p MODEL_PATH, --model-path MODEL_PATH
                        Model path
  -n, --no-pdf          No pdf render.
  -i CONCURRENT_PROCESS_COUNT, --concurrent-process-count CONCURRENT_PROCESS_COUNT
                        Number of concurrent process.
  -t CONCURRENT_THREAD_COUNT, --concurrent-thread-count CONCURRENT_THREAD_COUNT
                        Number of concurrent thread per process.
```

## Usage (slurm job)

Use template from `demo-predict.sh` and modify the command based on [Usage (interactive)](#usage-interactive).

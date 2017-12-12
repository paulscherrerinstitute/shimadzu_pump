# Shimadzu CBM20 pump IOC
IOC for controlling a single Shimadzu CBM20 pump. The library assumes that only 1 pump exists 
at the connection hostname.

## Available PVs

- \[IOC_PREFIX\] PUMPING (Read back value of the pump status)
- \[IOC_PREFIX\] PUMPING-SET (Set point for starting (write 1) or stopping (write 0) the pump)
- \[IOC_PREFIX\] FLOW (Read back value of the pump flow)
- \[IOC_PREFIX\] FLOW-SET (Set point for the pump flow)
- \[IOC_PREFIX\] MIN-PRESSURE (Read back value of the pump min pressure setting)
- \[IOC_PREFIX\] MIN-PRESSURE-SET (Set point for the pump min pressure setting)
- \[IOC_PREFIX\] MAX-PRESSURE (Read back value of the pump max pressure setting)
- \[IOC_PREFIX\] MAX-PRESSURE-SET (Set point for the pump max pressure setting)

## Quick start guide
```bash
# Install the library
conda install -c paulscherrerinstitute shimadzu_pump

# Run the IOC
schimadzu_pump_ioc IOC-PREFIX: PUMP_HOSTNAME.psi.ch
```

## Conda setup
If you use conda, you can create an environment with the shimadzu_pump library by running:

```bash
conda create -c paulscherrerinstitute --name <env_name> shimadzu_pump
```

After that you can just source you newly created environment and start using the library.

## Local build
You can build the library by running the setup script in the root folder of the project:

```bash
python setup.py install
```

or by using the conda also from the root folder of the project:

```bash
conda build conda-recipe
conda install --use-local shimadzu_pump
```

### Requirements
The library relies on the following packages:

- requests
- pcaspy

In case you are using conda to install the packages, you might need to add the **paulscherrerinstitute** channel to 
your conda config:

```
conda config --add channels paulscherrerinstitute
```

## RUN the IOC

Executable help:

```bash
usage: schimadzu_pump_ioc [-h] [--polling_interval POLLING_INTERVAL]
              [--log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
              ioc_prefix pump_host

positional arguments:
  ioc_prefix            Prefix of the IOC.
  pump_host             Pump host.

optional arguments:
  -h, --help            show this help message and exit
  --polling_interval POLLING_INTERVAL
                        Pump polling interval.
  --log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        Log level to use.
```

### Conda installation
To run the IOC, first install the conda package, and then execute:
```bash
# Run the IOC with the specified prefix.
schimadzu_pump_ioc IOC_PREFIX PUMP_HOSTNAME
```

### Manual installation
If you are not installing the conda package, you need to set this repo into your Python path. 
From the root of this repo run:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python schimadzu_pump/run.py IOC_PREFIX PUMP_HOSTNAME
```

**WARNING**: You need to make sure that all the requirements mentioned in the **Requirements** section are installed.

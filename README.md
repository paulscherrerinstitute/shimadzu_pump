# Shimadzu CBM20 pump IOC
Just a Shimadzu pump controller.

## Conda setup
If you use conda, you can create an environment with the mflow_nodes library by running:

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

### Conda installation
To run the IOC, first install the conda package, and then execute:
```bash
# Run the IOC with the specified prefix.
schimadzu_pump_ioc IOC_PREFIX
```

### Manual installation
If you are not installing the conda package, you need to run the IOC from the root folder of this repo:
```bash
python schimadzu_pump/run.py IOC_PREFIX
```

**WARNING**: You need to make sure that all the requirements mentioned in the **Requirements** section are installed.
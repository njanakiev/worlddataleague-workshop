# worlddataleague-2021

Working and Analysing OpenStreetMap for Data Science Projects

# Setup

You can run the notebooks either with docker or with anaconda environment.

## Docker Container

Install docker by following this [Guide](https://docs.docker.com/engine/install/ubuntu/) (Ubuntu). And this [guide](https://docs.docker.com/compose/install/) to install docker-compose.

Build and run with docker:

```bash
docker-compose -f docker/docker-compose.yml up --build
```
## Anaconda Environment

To install Anaconda download it from [here](https://www.anaconda.com/products/individual).

Create `wdl` Anaconda environment with:

```bash
conda env create -f environment.yml
conda activate wdl
jupyter-lab
```

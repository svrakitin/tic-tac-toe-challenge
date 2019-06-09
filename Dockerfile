FROM continuumio/miniconda3

SHELL ["/bin/bash", "-c"]

COPY environment.yml Makefile pytest.ini /source-code/

WORKDIR /source-code

RUN conda env create -f environment.yml

ENV CONDA_DEFAULT_ENV tictactoe
ENV PATH /opt/conda/envs/$CONDA_DEFAULT_ENV/bin:$PATH

RUN echo "conda activate $CONDA_DEFAULT_ENV" > ~/.bashrc

COPY tictactoe tictactoe
COPY tests tests

EXPOSE 8080
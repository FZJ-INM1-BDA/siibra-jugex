# siibra-jugex

## Siibra toolbox for atlas-based differential analysis of gene expressions

*Authors: Big Data Analytics Group and S. Bludau, Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH*

Copyright 2020-2021, Forschungszentrum Jülich GmbH 

> :warning: **`siibra-jugex` is at an experimental stage.** The software is not yet fully tested. Be aware that you will likely encounter bugs.

### Intro

JuGEx  (Julich-Brain Gene Expression) is an integrated framework developed to combined the AllenBrain and Julich-Brain atlases for statistical analysis of differential gene expression in the adult human brain.
The framework has been developed by S. Bludau et al. and is described in the following publication:

	Sebastian Bludau, Thomas W. Mühleisen, Simon B. Eickhoff, Michael J. Hawrylycz, Sven Cichon, Katrin Amunts. Integration of transcriptomic and cytoarchitectonic data implicates a role for MAOA and TAC1 in the limbic-cortical network. 2018, Brain Structure and Function. [https://doi.org/10.1007/s00429-018-1620-6](https://doi.org/10.1007/s00429-018-1620-6)

The original implementation in Matlab can be found [here](https://www.fz-juelich.de/SharedDocs/Downloads/INM/INM-1/DE/jugex.html?nn=2163780).

The basic idea of JuGExis to supplement different levels of information on brain architecture, e.g. structural and functional connectivity, brain activations, and neurotransmitter receptor density by transcriptional information to enlight biological aspects of brain organization and its diseases, spatially referring to the cytoarchitectonic Julich-Brain atlas. This allows analysis beyond approaches which rely on the traditional segregation of the brain into sulci and gyri, thereby combining functionally different microstructural areas. JuGex is publicly available to empower research from basic, cognitive and clinical neuroscience in further brain regions and disease models with regard to gene expression.

`siibra` is a Python client for interacting with "multilevel" brain atlases, which combine multiple brain parcellations, reference coordinate spaces and modalities. See [here](https://siibra.eu) for more details.
This siibra toolbox implements the JuGEx algorithm with siibra, to provide a simple and intuitive implementation in python, as well as an interactive plugin of the 3D atlas viewer of [EBRAINS](https://ebrains.eu/service/human-brain-atlas/).
The analysis is initialized with a siibra atlas object. It will check if the parcellation selected in the atlas is suitable for performing the analysis, which includes to verify that the given atlas object provides maps in the MNI ICBM 152 space. The analysis is configured by specifying some candidate genes of interest, and two regions of interest (ROI) specified by brain area names that the atlas object can resolve. Note that the siibra atlas class does fuzzy string matching to resolve region names, so you can try with a simple name of the regions to see if siibra interprets them.  Also, gene names can easily be looked up and autocompleted in siibra.gene_names.

For the gene expression data, `siibra-jugex` accesses the Allen Brain Atlas API (© 2015 Allen Institute for Brain Science. Allen Brain Atlas API. Available from: brain-map.org/api/index.html).

### Getting started

To get familiar with `siibra-jugex`, we recommend to checkout the notebook in the `examples/` subfolder of this repository. 

### Installation

`siibra-python` is available on pypi.
To install the latest version, simply run `pip install siibra-jugex`.

## Acknowledgements

This software code is funded from the European Union’s Horizon 2020 Framework
Programme for Research and Innovation under the Specific Grant Agreement No.
945539 (Human Brain Project SGA3).

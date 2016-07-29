# WorkingMemory_and_BrainStructure_Code
Data processing and statistical analysis scripts for the paper "Changes in brain morphology and working memory capacity over childhood"

The following files are contained in this repository: 
- CorticalThickness_Eigenanatomy_Decomposition.R: R script to run eigenanatomy decomposition on cortical thickness maps in common space using ANTsR
- FA_Eigenanatomy_Decomposition.R: R script to run eigenanatomy decomposition on FA maps in common space using ANTsR 
- WorkingMemory_FA_analysis.ipynb: IPython notebook containing the statistical analysis of FA results
- WorkingMemory_CorticalThickness_Analysis.ipynb : IPython notebook containing the statistical analysis of cortical thickness data


""""""""""""""""""""""""""""""""" 
## Description of the methods
"""""""""""""""""""""""""""""""""
_NB: The following description is taken from the Methods section of the paper_

3.4  Processing of diffusion-weighted data
Diffusion imaging makes it possible to quantify the rate of water diffusion in the brain. In the parallel bundles of white matter, diffusion is stronger along the fibre orientation, but is attenuated in the perpendicular direction. This can be summarized by the metric of fractional anisotropy (FA), which is a scalar value between 0 and 1 describing the degree of anisotropy of the diffusion at every voxel. Developmental studies show steady increases in FA between childhood and adulthood (Imperati et al., 2011, Muftuler et al., 2012, Westlye et al., 2009), which is likely to reflect increased myelination (Dean et al., 2014). 
A number of processing steps are necessary to derive FA maps from diffusion-weighted volumes. In the current study, diffusion-weighted MRI scans were converted from the native DICOM to compressed NIfTI-1 format using the dcm2nii tool http://www.mccauslandcenter.sc.edu/mricro/
mricron/dcm2nii.html. Subsequently, the images were submitted to the DiPy v0.8.0 implementation (Garyfallidis et al., 2014) of a non-local means de-noising algorithm (Coupe et al., 2008) to boost signal to noise ratio. Next, a brain mask of the b0 image was created using the brain extraction tool (BET) of the FMRIB Software Library (FSL) v5.0.8. Motion and eddy current correction were applied to the masked images using FSL routines. The corrected images were re-sliced to 1mm resolution with trilinear interpolation using in-house software based on NiBabel v2.0.0 functions (http://nipy.org/nibabel/). Finally, fractional anisotropy maps were created based on a diffusion tensor model fitted through the FSL dtifit algorithm (Behrens et al., 2003, Johansen-Berg et al., 2004). 
For comparison across participants, we created a study-specific FA-templates based on all available images using Advanced Normalization Tools (ANTs) algorithms (Lawson, Duda, Avants, Wu, & Farah, 2013, B. B. Avants et al., 2014), which showed the highest accuracy in software comparisons (Klein et al., 2009, Murphy et al., 2011, Tustison et al., 2014). Individual images were transformed to template space using non-linear registration with symmetric diffeomorphic normalization as implemented in ANTs (B. Avants, Epstein, Grossman, & Gee, 2008). Next, the images were eroded twice with a 3mm sphere to remove brain edge artefacts using FSL maths. 

3.5  Processing of T1-weighted data
Another measure of brain development that can be derived from neuroimaging data is cortical thickness (Giedd & Rapoport, 2010, Gogtay et al., 2004). Cortical thickness is defined as the distance between the outer edge of cortical grey matter and subcortical white matter (Fischl & Dale, 2000). To obtain thickness measure moments from anatomical MRI data, T1-weighted volumes were initially co-registered with MNI152 space using rigid co-registration in order to obtain good initial between-subject alignment and optimal field of view. Next, all images were visually inspected and images with pronounced motion artefact were removed from further analysis (n=31, 20.25% of the acquired data). The remaining data was submitted to the automatic ANTs cortical thickness pipeline (antsCorticalThickness). Details about the processing pipeline and thickness estimation are described in (Tustison et al., 2014) and (Das, Avants, Grossman, & Gee, 2009). Tissue priors were taken from the OASIS-TRT-20 template (http://www.mindboggle.info/data.html#mindboggle-software-data). Subsequently, images in template space were smoothed using a 10mm full width at half maximum (FWHM) Gaussian kernel and resampled to 2mm resolution. A thickness mask was created by averaging all images and binarizing the resulting mean image at a threshold of 

3.6  Eigenanatomy Decomposition
Traditional univariate approaches like voxel-based morphometry (VBM) fit a statistical model for every voxel in a brain image. Because of the large number of voxels in a typical imaging protocol, this approach necessitates correction for a very large number of comparisons (T1-volumes in the current study contained over 1 million voxels), resulting in a dramatic loss of statistical power. However, effects are typically spread over areas that are larger than 1 voxel. Multivariate approaches are better suited to reduce the dimensionality of the data to the information contained in the data itself before statistical comparisons are applied. Eigenanatomy Decomposition is a novel method for data-driven dimensionality reduction of neuroimaging data that adds sparseness and smoothness constraints for better anatomical interpretability in comparison to standard spatial principal component analysis (Kandel, Wang, Gee, & Avants, 2015). Cortical thickness masks and FA images were processed using the ANTsR v0.3.2 implementation of the Eigenanatomy Decomposition algorithm (Kandel et al., 2015). Parameters for Eigenanatomy Decomposition were adopted from published work, i.e. decomposition into 32 components with sparseness of 1/32 with 20 iterations, a L1 penalty with gradient step size 0.5, a smoothing kernel of 1 voxel, and a minimum cluster size of 1000 voxels for each eigenvector. For statistical analysis, the mean value of each brain morphology measure (FA, cortical thickness) within each eigenanatomy component was calculated. 

3.7  Statistical analysis
We wanted to test how brain morphology was associated with the components of the working memory system, and the extent to which this relationship was moderated by age. The relationship between these factors was therefore tested in the following set of regression models: a) age predicting working memory performance, b) age predicting brain morphology measures, c) brain morphology predicting working memory; and ultimately d) the interaction between brain morphology and age predicting working memory (see Figure 2for an overview of these models). Gender and an intercept term were included as additional regressors in each model. Assessment of Cook’s distance (Cook, 1977) indicated no particularly influential data points in the regression models. Therefore, all available data points were retained in the analysis. Regression analysis was carried out using the ’stats’ package v3.1.2 in Rbase.



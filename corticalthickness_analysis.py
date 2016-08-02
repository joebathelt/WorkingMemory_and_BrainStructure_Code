# Running cortical thickness analysis
import os
import re
import shutil
import CALM_utils
import T1_workflows 

# CALM
T1_files = CALM_utils.get_list_of_BIDS_files('/imaging/jb07/CALM/CALM_BIDS/','T1w')
subject_list = sorted([T1_file.split('/')[-1].split('_')[0] for T1_file in T1_files])
incomplete_subjects = list()

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'
for subject in subject_list:
	if not os.path.isfile(folder + '_subject_id_' + subject + '/corticalthickness/' + subject + 'CorticalThicknessNormalizedToTemplate.nii.gz'):
		incomplete_subjects.append(subject)

T1_workflows.ANTs_cortical_thickness(subject_list,'/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/')

# ACE
T1_files = CALM_utils.get_list_of_BIDS_files('/imaging/aj05/ACE_DTI_data/original_BIDS/', 'T1w')
subject_list = sorted([T1_file.split('/')[-1].split('_')[0] for T1_file in T1_files])
incomplete_subjects = list()

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'
for subject in subject_list:
	if not os.path.isfile(folder + '_subject_id_' + subject + '/corticalthickness/' + subject + 'CorticalThicknessNormalizedToTemplate.nii.gz'):
		incomplete_subjects.append(subject)

T1_workflows.ANTs_cortical_thickness(incomplete_subjects,'/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/')

# Moving files to new folder
folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'
outfolder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/results/'

for subfolder in os.listdir(folder):
	subject = subfolder.split('_')[-1]

	if os.path.isfile(folder + subfolder + '/corticalthickness/' + subject + 'CorticalThicknessNormalizedToTemplate.nii.gz'):
		shutil.copyfile(folder + subfolder + '/corticalthickness/' + subject + 'CorticalThicknessNormalizedToTemplate.nii.gz', 
					    outfolder + subject + '.nii.gz')

	if os.path.isfile(folder + subfolder + '/corticalthickness/' + subject + 'CorticalThicknessTiledMosaic.png'):
		shutil.copyfile(folder + subfolder + '/corticalthickness/' + subject + 'CorticalThicknessTiledMosaic.png',
			'/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/results_overview/' + subject + '.png')


# Moving the processed files to the results folder 
import os
import re
import shutil

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'

for subfolder in os.listdir(folder):
	if os.path.isdir(folder + subfolder + '/corticalthickness/'):
		subject = subfolder.split('_')[-1]
		in_file = folder + subfolder + '/corticalthickness/' + subject + 'CorticalThickness.nii.gz'
		out_file = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/results/' + subject + '.nii.gz'

		if os.path.isfile(in_file):
			shutil.copyfile(in_file,out_file)

# Moving the processed files to the results folder 
import os
import re
import shutil

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'

for subfolder in os.listdir(folder):
	if os.path.isdir(folder + subfolder + '/at/'):
		subject = subfolder.split('_')[-1]
		in_file = folder + subfolder + '/at/' + subject + 'BrainSegmentation0N4_gm_density_trans.nii.gz'
		out_file = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/GM_densities/' + subject + '.nii.gz'

		if os.path.isfile(in_file):
			shutil.copyfile(in_file,out_file)

# Making an overview of the results
# Bash slicesdir *.nii.gz

# Creating a thickness mask
import os 
import nibabel as nib
import numpy as np

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/results/'
subject_list = [subject for subject in os.listdir(folder)]
data = list()

for subject in subject_list:
	img = nib.load(folder + subject)
	data.append(img.get_data())

data = np.array(data)
data[data > 0] = 1
mean_data = np.sum(data,axis=0)/data.shape[0]
mean_data[mean_data > 0.1] = 1
mean_data[mean_data < 0.1] = 0

img = nib.load('/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors2.nii.gz')
cortical_mask = img.get_data()

mean_data = mean_data*cortical_mask
nib.save(nib.Nifti1Image(mean_data,img.get_affine()),'/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/GM_mask.nii.gz')

# Calculating intracranial volume
import T1_workflows
import CALM_utils
reload(T1_workflows)
folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/antsthickness/'
out_folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/intracranial_volume/'
T1_files = CALM_utils.get_list_of_BIDS_files('/imaging/jb07/CALM/CALM_BIDS/','T1w')
subject_list = sorted([T1_file.split('/')[-1].split('_')[0] for T1_file in T1_files])

for subject in subject_list:
	if os.path.isfile(folder + '_subject_id_' + subject + '/corticalthickness/' + subject + 'CorticalThicknessNormalizedToTemplate.nii.gz'):
		shutil.copyfile(folder + '_subject_id_' + subject + '/corticalthickness/' + subject + 'ExtractedBrain0N4.nii.gz', 
						'/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/intracranial_volume/' + subject + '.nii.gz')

subject_list = [subject.split('.')[0] for subject in os.listdir(out_folder)]
T1_workflows.get_ICV(subject_list, out_folder)

import numpy as np
import pandas as pd
import re
import os

folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/CorticalThickness3/intracranial_volume/get_ICV/'
subject_list = [subject.split('_')[-1] for subject in os.listdir(folder) if re.search('_subject_id_', subject)]
ICVs = list()
subjects = list()

for subject in subject_list:
	ICVs.append(np.loadtxt(folder + '_subject_id_' + subject + '/mat2det/' + subject + '_ICV.txt')[1])
	subjects.append(subject)

df = pd.DataFrame({'MRI.ID':subjects, 'ICV':ICVs})
df.to_csv('/home/jb07/Desktop/ICVs.csv')
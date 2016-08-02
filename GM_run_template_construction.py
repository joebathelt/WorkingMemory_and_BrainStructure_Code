# Creating the average template and transformations for all participants
import os
import re
from nipype.interfaces.ants.legacy import buildtemplateparallel
out_folder = '/imaging/jb07/WorkingMemory_Analysis/analysis_Mar2016/GM_study_template/template/template_building/'
in_files = [subject for subject in os.listdir(out_folder) if re.search('.nii.gz', subject)]

os.chdir(out_folder)
in_files = in_files
tmpl = buildtemplateparallel()
tmpl.inputs.in_files = in_files
tmpl.inputs.use_first_as_target = False
tmpl.inputs.bias_field_correction = True
tmpl.inputs.max_iterations = [30, 90, 20]
tmpl.inputs.parallelization = 2
tmpl.inputs.num_cores = len(in_files)
tmpl.run()

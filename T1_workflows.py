def ANTs_Apply_Transform(subject_list,base_directory,reference):
	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	from nipype import SelectFiles
	from nipype.interfaces.ants import ApplyTransforms
	import os

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(in_file = 'antsTMPL_{subject_id}repaired.nii.gz',
					 warp_field = 'antsTMPL_{subject_id}Warp.nii.gz',
					 transformation_matrix = 'antsTMPL_{subject_id}Affine.txt')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(base_directory)

	at = pe.Node(interface=ApplyTransforms(), name='at')
	at.inputs.dimension = 3
	at.inputs.reference_image = reference
	at.inputs.interpolation = 'Linear'
	at.inputs.default_value = 0
	at.inputs.invert_transform_flags = False

	#====================================
	# Setting up the workflow
	apply_ants_transform = pe.Workflow(name='apply_ants_transform')

	apply_ants_transform.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	apply_ants_transform.connect(selectfiles, 'in_file', at, 'input_image')
	apply_ants_transform.connect(selectfiles, 'warp_field', at, 'transforms')

	#====================================
	# Running the workflow
	apply_ants_transform.base_dir = os.path.abspath(base_directory)
	apply_ants_transform.write_graph()
	apply_ants_transform.run('PBSGraph')
	
def ANTs_cortical_thickness(subject_list,directory):

	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	import own_nipype
	from nipype.interfaces.ants.segmentation import antsCorticalThickness
	from nipype.interfaces.ants import ApplyTransforms
	from nipype.interfaces.ants import MultiplyImages
	from nipype.interfaces.utility import Function
	from nipype.interfaces.ants.visualization import ConvertScalarImageToRGB
	from nipype.interfaces.ants.visualization import CreateTiledMosaic
	from nipype.interfaces.utility import Select
	from own_nipype import GM_DENSITY
	from nipype import SelectFiles
	import os

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(T1='/imaging/jb07/CALM/CALM_BIDS/{subject_id}/anat/{subject_id}_T1w.nii.gz')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(directory)

	# Rigid alignment with the template space
	T1_rigid_quickSyN = pe.Node(interface=own_nipype.ants_QuickSyN(image_dimensions=3, transform_type='r'), name='T1_rigid_quickSyN')
	T1_rigid_quickSyN.inputs.fixed_image = '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0.nii.gz'

    # Cortical thickness calculation
	corticalthickness = pe.Node(interface=antsCorticalThickness(), name='corticalthickness')
	corticalthickness.inputs.brain_probability_mask = '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0_BrainCerebellumProbabilityMask.nii.gz'
	corticalthickness.inputs.brain_template= '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0.nii.gz'
	corticalthickness.inputs.segmentation_priors = ['/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors1.nii.gz',
	                                                '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors2.nii.gz',
	                                                  '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors3.nii.gz',
	                                                  '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors4.nii.gz',
	                                                   '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors5.nii.gz',
	                                                '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/Priors2/priors6.nii.gz']
	corticalthickness.inputs.extraction_registration_mask = '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0_BrainCerebellumExtractionMask.nii.gz'
	corticalthickness.inputs.t1_registration_template = '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0_BrainCerebellum.nii.gz'

	# Creating visualisations for quality control
	converter = pe.Node(interface=ConvertScalarImageToRGB(), name='converter')
	converter.inputs.dimension = 3
	converter.inputs.colormap = 'cool'
	converter.inputs.minimum_input = 0
	converter.inputs.maximum_input = 5

	mosaic_slicer = pe.Node(interface=CreateTiledMosaic(), name='mosaic_slicer')
	mosaic_slicer.inputs.pad_or_crop = 'mask'
	mosaic_slicer.inputs.slices = '[4 ,mask , mask]'
	mosaic_slicer.inputs.direction = 1
	mosaic_slicer.inputs.alpha_value = 0.5

	# Getting GM density images
	gm_density = pe.Node(interface=GM_DENSITY(), name='gm_density')
	sl = pe.Node(interface=Select(index=1), name='sl')

	# Applying transformation
	at = pe.Node(interface=ApplyTransforms(), name='at')
	at.inputs.dimension = 3
	at.inputs.reference_image = '/imaging/jb07/Atlases/OASIS/OASIS-30_Atropos_template/T_template0_BrainCerebellum.nii.gz'
	at.inputs.interpolation = 'Linear'
	at.inputs.default_value = 0
	at.inputs.invert_transform_flags = False

	# Multiplying the normalized image with Jacobian
	multiply_images = pe.Node(interface=MultiplyImages(dimension=3), name='multiply_images')

	# Naming the output of multiply_image
	def generate_filename(subject_id):
		return subject_id + '_multiplied.nii.gz'

	generate_filename = pe.Node(interface= Function(input_names=["subject_id"],
						                             output_names=["out_filename"],
						                             function=generate_filename), 
								name='generate_filename')

	#====================================
	# Setting up the workflow
	antsthickness = pe.Workflow(name='antsthickness')

	antsthickness.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	antsthickness.connect(selectfiles, 'T1', T1_rigid_quickSyN, 'moving_image')
	antsthickness.connect(infosource, 'subject_id', T1_rigid_quickSyN, 'output_prefix')
	antsthickness.connect(T1_rigid_quickSyN, 'warped_image', corticalthickness, 'anatomical_image')
	antsthickness.connect(infosource, 'subject_id', corticalthickness, 'out_prefix')
	antsthickness.connect(corticalthickness, 'CorticalThickness', converter, 'input_image')
	antsthickness.connect(converter, 'output_image', mosaic_slicer, 'rgb_image')
	antsthickness.connect(corticalthickness, 'BrainSegmentationN4', mosaic_slicer, 'input_image')
	antsthickness.connect(corticalthickness, 'BrainExtractionMask', mosaic_slicer, 'mask_image')

	antsthickness.connect(corticalthickness, 'BrainSegmentationN4', gm_density, 'in_file')
	antsthickness.connect(corticalthickness, 'BrainSegmentationPosteriors', sl, 'inlist')
	antsthickness.connect(sl, 'out', gm_density, 'mask_file')
	antsthickness.connect(corticalthickness, 'SubjectToTemplate1Warp', at, 'transforms')
	antsthickness.connect(gm_density, 'out_file', at, 'input_image')
	antsthickness.connect(corticalthickness, 'SubjectToTemplateLogJacobian', multiply_images, 'second_input')
	antsthickness.connect(corticalthickness, 'CorticalThicknessNormedToTemplate', multiply_images, 'first_input')
	antsthickness.connect(infosource, 'subject_id', generate_filename, 'subject_id')
	antsthickness.connect(generate_filename, 'out_filename',  multiply_images, 'output_product_image')
	
	#====================================
	# Running the workflow
	antsthickness.base_dir = os.path.abspath(directory)
	antsthickness.write_graph()
	antsthickness.run('PBSGraph')

def coreg_with_FLIRT(subject_list,base_directory):
	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	from nipype import SelectFiles
	from nipype.interfaces import fsl
	import os

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(in_file='{subject_id}.nii.gz')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(base_directory)

	flt = pe.Node(interface=fsl.FLIRT(dof=6, cost_func='corratio'), name='flt')
	flt.inputs.reference = os.environ['FSLDIR'] + '/data/standard/FMRIB58_FA_1mm.nii.gz'

	#====================================
	# Setting up the workflow
	flt_coreg = pe.Workflow(name='flt_coreg')

	flt_coreg.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	flt_coreg.connect(selectfiles, 'in_file', flt, 'in_file')

	#====================================
	# Running the workflow
	flt_coreg.base_dir = os.path.abspath(base_directory)
	flt_coreg.write_graph()
	flt_coreg.run('PBSGraph')

def FreeSurfer_Reconall(subject_list,base_directory,out_directory):
	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	from nipype.interfaces.freesurfer import ReconAll
	from nipype import SelectFiles
	import os
	nodes = list()

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(T1='{subject_id}/anat/{subject_id}_T1w.nii.gz')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(base_directory)
	nodes.append(selectfiles)


	reconall = pe.Node(interface=ReconAll(), name='reconall')
	reconall.inputs.directive = 'autorecon2'
	reconall.inputs.subjects_dir = out_directory
	reconall.inputs.flags = '-no-isrunning'
	reconall.inputs.ignore_exception = True

	# Setting up the workflow
	fs_reconall = pe.Workflow(name='fs_reconall')

	# Reading in files
	fs_reconall.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	fs_reconall.connect(selectfiles, 'T1', reconall, 'T1_files')
	fs_reconall.connect(infosource, 'subject_id', reconall, 'subject_id')


	# Running the workflow
	fs_reconall.base_dir = os.path.abspath(out_directory)
	fs_reconall.write_graph()
	fs_reconall.run('PBSGraph')


def get_ICV(subject_list,base_directory):
	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	from nipype.algorithms import misc
	from nipype import SelectFiles
	from nipype.interfaces import fsl
	from own_nipype import MAT2DET
	import os

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(in_file= '/imaging/jb07/CALM/CALM_BIDS/{subject_id}/anat/{subject_id}_T1w.nii.gz')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(base_directory)

	# Segment the image with FSL FAST
	fast = pe.Node(interface=fsl.FAST(), name='fast')
	fast.inputs.img_type = 1
	fast.inputs.no_bias = True

	# Select files from the FAST output
	GM_select = pe.Node(interface=util.Select(index = [1]), name='GM_select')
	WM_select = pe.Node(interface=util.Select(index = [2]), name='WM_select')

	# Calculate GM and WM volume with FSL stats
	GM_volume = pe.Node(interface=fsl.ImageStats(), name='GM_volume')
	GM_volume.inputs.op_string = '-M -V'

	WM_volume = pe.Node(interface=fsl.ImageStats(), name = 'WM_volume')
	WM_volume.inputs.op_string = '-M -V'

	flt = pe.Node(interface=fsl.FLIRT(), name='flt')
	flt.inputs.reference = os.environ['FSLDIR'] + '/data/standard/MNI152_T1_1mm_brain.nii.gz'

	mat2det = pe.Node(interface=MAT2DET(), name='mat2det')

	# Create an output csv file
	addrow = pe.Node(interface=misc.AddCSVRow(), name='addrow')
	addrow.inputs.in_file = base_directory + 'volume_results.csv'

	#====================================
	# Setting up the workflow
	get_ICV = pe.Workflow(name='get_ICV')
	get_ICV.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	#get_ICV.connect(selectfiles, 'in_file', flt, 'in_file')
	#get_ICV.connect(flt, 'out_matrix_file', mat2det, 'in_matrix')
	#get_ICV.connect(infosource, 'subject_id', mat2det, 'subject_id')
	get_ICV.connect(infosource, 'subject_id', fast, 'out_basename')
	get_ICV.connect(selectfiles, 'in_file', fast, 'in_files')
	get_ICV.connect(fast, 'partial_volume_files', GM_select, 'inlist')
	get_ICV.connect(GM_select, 'out', GM_volume, 'in_file')
	get_ICV.connect(fast, 'partial_volume_files', WM_select, 'inlist')
	get_ICV.connect(WM_select, 'out', WM_volume, 'in_file')
	get_ICV.connect(infosource, 'subject_id', addrow, 'MRI.ID')
	get_ICV.connect(GM_volume, 'out_stat', addrow, 'GM_volume')
	get_ICV.connect(WM_volume, 'out_stat', addrow, 'WM_volume')

	#====================================
	# Running the workflow
	get_ICV.base_dir = os.path.abspath(base_directory)
	get_ICV.write_graph()
	get_ICV.run('PBSGraph')

def T1_template_preproc(subject_list, base_directory, out_directory):
	#==============================================================
	# Loading required packages
	import nipype.interfaces.io as nio
	import nipype.pipeline.engine as pe
	import nipype.interfaces.utility as util
	from nipype import SelectFiles
	from nipype.interfaces import fsl
	import os

	#====================================
	# Defining the nodes for the workflow

	# Getting the subject ID
	infosource  = pe.Node(interface=util.IdentityInterface(fields=['subject_id']),name='infosource')
	infosource.iterables = ('subject_id', subject_list)

	# Getting the relevant diffusion-weighted data
	templates = dict(T1='{subject_id}/anat/{subject_id}_T1w.nii.gz')

	selectfiles = pe.Node(SelectFiles(templates),
	                   name="selectfiles")
	selectfiles.inputs.base_directory = os.path.abspath(base_directory)

	btr =  pe.Node(interface=fsl.BET(), name='betr')
	btr.inputs.robust = True

	flt = pe.Node(interface=fsl.FLIRT(dof=6, cost_func='corratio'), name='flt')
	flt.inputs.reference = os.environ['FSLDIR'] + '/data/standard/MNI152_T1_1mm_brain.nii.gz'

	robustfov = pe.Node(interface=fsl.RobustFOV(), name='robustfov')

	#====================================
	# Setting up the workflow
	templ_preproc = pe.Workflow(name='templ_preproc')

	templ_preproc.connect(infosource, 'subject_id', selectfiles, 'subject_id')
	templ_preproc.connect(selectfiles, 'T1', btr, 'in_file')
	templ_preproc.connect(btr, 'out_file', flt, 'in_file')
	templ_preproc.connect(flt, 'out_file', robustfov, 'in_file')

	#====================================
	# Running the workflow
	templ_preproc.base_dir = os.path.abspath(out_directory)
	templ_preproc.write_graph()
	templ_preproc.run('PBSGraph')
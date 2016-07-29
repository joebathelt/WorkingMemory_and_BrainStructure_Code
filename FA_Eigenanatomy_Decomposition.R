require(ANTsR)

in_folder = '/Users/joebathelt1/Documents/Other_Projects/CALM/images_in_template_space/'
setwd(in_folder)
images <- list()
for (image in list.files(in_folder)){
	images[[image]] <- antsImageRead(image)
}

mask <- getMask(images[[1]], 
			  	lowThresh = 0.2,
			  	highThresh = 1,
			  	cleanup = TRUE)

mat  <- imageListToMatrix(images, mask)

# Eigenanatomy decomposition
eanat <- sparseDecom(inmatrix = mat,
					 inmask = mask,
					 verbose = TRUE)

eseg <- eigSeg(mask = mask,
			imgList = eanat$eigenanatomyimages,
			applySegmentationToImage = FALSE)

antsImageWrite(eseg,paste('/Users/joebathelt1/Desktop/Eigenanatomy_test/Eigenanatomy_segmentation.nii.gz'))

# Doing statistics within eigenanatomy regions
segmentation <- imageListToMatrix(imageList=c(eseg), mask=mask)
eigenanatomy_components <- sort(unique(c(segmentation)))[(2:length(unique(c(segmentation))))]

# Transferring eigenanatomy decomposition to images
eigenanatomyImages <- matrixToImages(eanat$eigenanatomyimages, mask=mask)

for (i in 1:length(eigenanatomyImages)){
	antsImageWrite(eigenanatomyImages[[i]],paste('/Users/joebathelt1/Desktop/Eigenanatomy_test/EigenanatomyComp',i,'.nii.gz', sep=""))
}

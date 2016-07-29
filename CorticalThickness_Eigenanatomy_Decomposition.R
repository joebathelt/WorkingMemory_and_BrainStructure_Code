require(ANTsR)

in_folder = '/Users/joebathelt1/Documents/Other_Projects/CALM/Thickness_in_template_space'
mask = '/Users/joebathelt1/Documents/Other_Projects/CALM/GM_mask.nii.gz'

setwd(in_folder)
images <- list()
for (image in list.files(in_folder)){
    images[[image]] <- antsImageRead(image)
}

mask <- antsImageRead(mask)
mask_matrix <- imageListToMatrix(imageList=c(mask), mask=mask)
mask <- getMask(mask, 
                  lowThresh = 1,
                  highThresh = 1,
                  cleanup = TRUE)

mat  <- imageListToMatrix(images, mask)

# Eigenanatomy decomposition
eanat <- sparseDecom(inmatrix = mat,
                     inmask = mask,
                     nvecs = 32,
                     sparseness = 1/32,
                     its = 2,
                     smooth = 1,
                     cthresh = 1000,
                     ell1 = 0.5,
                     verbose = TRUE)

eseg <- eigSeg(mask = mask,
            imgList = eanat$eigenanatomyimages,
            applySegmentationToImage = FALSE)

antsImageWrite(eseg,paste('/Users/joebathelt1/Documents/Other_Projects/CALM/Thickness_segmentation.nii.gz'))

# Doing statistics within eigenanatomy regions
segmentation <- imageListToMatrix(imageList=c(eseg), mask=mask)
eigenanatomy_components <- sort(unique(c(segmentation)))[(2:length(unique(c(segmentation))))]

# Transferring eigenanatomy decomposition to images
eigenanatomyImages <- matrixToImages(eanat$eigenanatomyimages, mask=mask)

for (i in 1:length(eigenanatomyImages)){
    antsImageWrite(eigenanatomyImages[[i]],paste('/Users/joebathelt1/Documents/Other_Projects/CALM/Thickness_components/EigenanatomyComp',i,'.nii.gz', sep=""))
}

save(eanat,file='/Users/joebathelt1/Documents/Other_Projects/CALM/Thickness_components/Eigenanatomy_eanat.R')
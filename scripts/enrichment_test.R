#!/usr/bin/Rscript
args <- commandArgs(TRUE)
# Define query folder
directory <- args[1]

# Read in database
db <- read.csv("db.csv",header=T,row.names=1)

# Read in user's input list of genes
input <- read.delim(paste(directory,'ids.txt', sep=''),header=F)
input <- as.character(input[,1]) # convert dataframe to vector of characters

# Separate comparisons into two groups: quantitative versus categorical
quantitative <- vector()
categorical <- vector()

for(x in c(1:ncol(db))) {
	if(unclass(class(db[,x])) == "integer" || unclass(class(db[,x])) == "numeric") {
		quantitative <- append(quantitative,colnames(db)[x])
	} 
	if(unclass(class(db[,x])) == "logical") {
		categorical <- append(categorical,colnames(db)[x])
	}
}

# ncol(db) = 99, length(c(quantitative,categorical)) = 93
# The 6 missing columns come from e.g. genename,sgid,genetype,etc 
# These are ignored in the enrichment analysis

# Remove orif from quantitative
quantitative <- quantitative[-which(quantitative=="orfid")] 

# Perform enrichment analysis for each quantitative column 
# Using Wilcox Rank-Sum Test

quant.wilcox <- matrix(ncol=2,nrow=length(quantitative))
row.names(quant.wilcox) <- quantitative
colnames(quant.wilcox) <- c("pvalue","difference")

for(x in c(1:length(quantitative))) {
	quant.wilcox[x,1] <- wilcox.test(db[,quantitative[x]],db[input,quantitative[x]],na.rm=T)$p.value
	quant.wilcox[x,2] <- median(db[input,quantitative[x]],na.rm=T) - median(db[,quantitative[x]],na.rm=T)
}

# Correct for multiple comparisons using Benjamini-Hochberg FDR method
quant.wilcox[,1] <- p.adjust(quant.wilcox[,1],method="fdr")
quant.wilcox <- quant.wilcox[order(quant.wilcox[,1]),]
quant.wilcox[,1] <- signif(quant.wilcox[,1],1)

# Write quantitative enrichment results
quant.basefilename = "quant_enrichment.csv"
quant.filename = paste(directory,quant.basefilename,sep="")
write.csv(quant.wilcox,file=quant.filename)

# Perform enrichment analysis for each categorical column
# Using Fisher's exact test

fisherit <- function(column,dataone=row.names(db),datatwo) {
	contingencytable <- matrix(ncol=2,nrow=2)
	contingencytable[2,1] <- sum(db[dataone,column],na.rm=T)
	contingencytable[2,2] <- length(dataone) - contingencytable[2,1]
		# We are treating NA's as false
	contingencytable[1,1] <- sum(db[datatwo,column],na.rm=T)
	contingencytable[1,2] <- length(datatwo) - contingencytable[1,1]
	return(fisher.test(contingencytable))
	# an estimate > 1 means datatwo is enriched in TRUEs compared to dataone
}

cat.fisher <- matrix(ncol=2,nrow=length(categorical))
row.names(cat.fisher) <- categorical
colnames(cat.fisher) <- c("pvalue","ratio")

for(x in c(1:length(categorical))) {
	result <- fisherit(column=categorical[x],datatwo=input)
	cat.fisher[x,1] <- result$p.value
	cat.fisher[x,2] <- result$estimate 
}	

# Correct for multiple comparisons using FDR method
cat.fisher[,1] <- p.adjust(cat.fisher[,1],method="fdr")
cat.fisher <- cat.fisher[order(cat.fisher[,1]),]
cat.fisher[,1] <- signif(cat.fisher[,1],1)

# Write categorical enrichment results
cat.basefilename = "cat_enrichment.csv"
cat.filename = paste(directory,cat.basefilename,sep="")
write.csv(cat.fisher,file=cat.filename)

# Look for interesting genes in each category 
# Using percentile cutoff, "type 2" which is the intuitive quantile cutoff (not estimating it from a density)
#cutoffone = 0.05 #top 5% and bottom 5%
#cutofftwo = 0.10 #top 10% and bottom 10%

#quant.quantile <- matrix(ncol=4,nrow=length(quantitative))
# numbers above or below this are in the top or bottom percentile
# bottom 5%, top 5%, bottom 10%, top 10%

#for(x in c(1:length(quantitative))) {
#	quant.quantile[x,] <- quantile(db[,quantitative[x]],c(cutoffone,1-cutoffone,cutofftwo,1-cutofftwo),type=2,na.rm=T)
#}

# at 10% cutoff (either bottom 10% or top 10%)

#interestinggenes <- matrix(ncol=length(quantitative),nrow=nrow(db))
#row.names(interestinggenes) <- row.names(db)
#colnames(interestinggenes) <- quantitative
#
#for(x in c(1:length(quantitative))) {
#	bottom <- which(db[,quantitative[x]] < quant.quantile[x,3])
#	top <- which(db[,quantitative[x]] > quant.quantile[x,4])
#	interestinggenes[,x] <- 0
#	interestinggenes[bottom,x] <- -1
#	interestinggenes[top,x] <- 1
#}

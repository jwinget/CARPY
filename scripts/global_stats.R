# Read in the database
print('Reading database')
d <- read.csv('db.csv', header=TRUE)

# Create a list of amino acid names
aminoacids <- c('ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly', 'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'ser', 'thr', 'trp', 'tyr', 'val')

# Add the percent amino acid columns to the data frame
print('Adding percentage columns for amino acids')
for(aa in aminoacids) {
	colname = paste('perc_', aa, sep='')
	d[,colname] <- c(d[,aa]/d$proteinlength)
}

# Test for quantitative columns
print('Auto-detecting quantitative columns')
quantcols = c()
for(n in c(names(d))) {
	cl = class(d[,n])
	if(cl=='numeric' || cl=='integer') {
		quantcols = c(quantcols, n)
	}
}

# Create a data frame to hold fivenum values
fn_cols <- c('min','lowerhinge','median','upperhinge','max')
fn <- data.frame(t(rep(NA,length(fn_cols))))
names(fn) <- fn_cols
fn <- fn[-1,]

# Calculate fivenum on each quantitative column
print('Calculating fivenums')
for(i in c(1:length(quantcols))) {
	col = quantcols[i]
	result <- c(fivenum(d[,col]))
	fn[i,] <- result
	}
row.names(fn) <- quantcols

# write out the csv file
write.csv(fn, file='fivenums.csv')

# Produce boxplots of each numerical column
print('Generating boxplots of numerical data')
outdir = 'images/'
for(col in quantcols) {
	outfile = paste(outdir,col,'_boxplot.png',sep='')
	png(outfile)
	boxplot(d[,col], main=col, na.rm=TRUE)
	dev.off()
	}

print('Done')

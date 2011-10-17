# Read in the database
print('Reading database')
d <- read.table('db.txt', header=TRUE, row.names=1)

# Create a list of amino acid names
#aminoacids <- c('ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly', 'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'ser', 'thr', 'trp', 'tyr', 'val')
#
## Add the percent amino acid columns to the data frame
#print('Adding percentage columns for amino acids')
#for(aa in aminoacids) {
#	colname = paste('perc_', aa, sep='')
#	d[,colname] <- c(d[,aa]/d$proteinlength)
#}

# Test for quantitative columns
print('Auto-detecting quantitative columns')
quantcols = c()
for(n in c(names(d))) {
	cl = class(d[,n])
	if(cl=='numeric' || cl=='integer') {
		quantcols = c(quantcols, n)
	}
}

# Calculate percentiles
print('Calculating percentiles')
for(col in quantcols) {
	colname = paste(col, '_percentiles', sep='')
	d[,colname] <- c(100*(rank(d[,col])/length(d[,col])))
	}

# write out the csv file
write.csv(d, file='db_updated.csv')

# Generate density plots for each numeric column
# Show location of protein of interest on plot
print('Generating plots of each property')

# Out directory should also be variable, to save queries in individual folders
for(p in row.names(d)){
	outdir = paste('img/',p,'/',sep='')
	dir.create('img')
	dir.create(outdir)
	for(col in quantcols) {
		outfile = paste(outdir,p,'_',col,'_density.png',sep='')
		png(outfile)
		plot(density(d[,col], na.rm=TRUE), main=col, log='x', lwd=2)
		abline(v=d[p,col], col='red', lty='dashed', lwd=2)
		dev.off()
		}
	}

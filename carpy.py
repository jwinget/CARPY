from flask import Flask, render_template, request, redirect, url_for
from mongokit import Connection, Document
import uuid
import os
import subprocess
import csv
import smtplib

#---- Reverse Proxy Fix ----#
class ReverseProxied(object):
	def __init__(self, app):
		self.app = app
	def __call__(self, environ, start_response):
		script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
		if script_name:
			environ['SCRIPT_NAME'] = script_name
			path_info = environ['PATH_INFO']
			if path_info.startswith(script_name):
				environ['PATH_INFO'] = path_info[len(script_name):]

		scheme = environ.get('HTTP_X_SCHEME', '')
		if scheme:
			environ['wsgi.url_scheme'] = scheme
		return self.app(environ, start_response)

#---- Configuration ----#
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object(__name__)

app.debug = True

#---- Mongo Connection ----#
connection = Connection(app.config['MONGODB_HOST'],
						app.config['MONGODB_PORT'])

#---- Models ----#
class Protein(Document):
	''' The structure of the document comes from the CSV which we import externally.
	Fields can be accessed using their names from the header line of the CSV file. '''
	use_dot_notation = True

# Register the Protein document with our current connection
connection.register([Protein])

# This connects to the pre-existing database Carpy and collection Proteins
collection = connection['Carpy'].Proteins

#---- Functions ----#
def send_email(sender, receiver, subject, body):
	msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" %(sender, receiver, subject, body))
	s = smtplib.SMTP('localhost')
	s.sendmail(sender, [receiver], msg)
	s.quit()

def protein_query(i):
	i = i.upper()
	genename_query = collection.find_one({'genename': i})
	if genename_query is not None:
		return genename_query
	sys_query = collection.find_one({'systematicname': i})
	if sys_query is not None:
		return sys_query
	sgid_query = collection.find_one({'sgid': i})
	if sgid_query is not None:
		return sgid_query

#---- Misc ----#
name_dict = {
'genename':'Gene Name',
'sgid':'SGID',
'molecularweight':'Molecular Weight',
'pi':'Isoelectric Point',
'cai':'Codon Adaptation Index',
'proteinlength':'Protein Length',
'codonbias':'Codon Bias',
'ala':'Alanines',
'arg':'Arginines',
'asn':'Asparagines',
'asp':'Aspartic Acids',
'cys':'Cysteines',
'gln':'Glutamines',
'glu':'Glutamic Acids',
'gly':'Glycines',
'his':'Histidines',
'ile':'Isoleucines',
'leu':'Leucines',
'lys':'Lysines',
'met':'Metionines',
'phe':'Phenylalanines',
'pro':'Prolines',
'ser':'Serines',
'thr':'Threonines',
'trp':'Tryptophans',
'tyr':'Tyrosines',
'val':'Valines',
'fopscore':'Freq of Optimal Codons Score',
'gravyscore':'GRAVY Score',
'aromaticityscore':'Aromaticity Score',
'genetype':'Gene Type',
'orfid':'ORF ID',
'abundance':'Protein Abundance',
'localization':'Localization',
'ambiguous':'Ambiguous Localization',
'mitochondrion':'In Mitochondria',
'vacuole':'In Vacuole',
'spindlepole':'At Spindle Pole',
'cellperiphery':'At Cell Periphery',
'punctatecomposite':'At Punctate Composite',
'vacuolarmembrane':'In Vacuolar Membrane',
'er':'In Endoplasmic Reticulum',
'nuclearperiphery':'At Nuclear Periphery',
'endosome':'In Endosome',
'budneck':'At Bud Neck',
'microtubule':'Near Microtubules',
'golgi':'In Golgi',
'lategolgi':'In Late Golgi',
'peroxisome':'In Peroxisome',
'actin':'Near Actin',
'nucleolus':'In Nucleolus',
'cytoplasm':'In Cytoplasm',
'ertogolgi':'In ER to Golgi Transition',
'earlygolgi':'In Early Golgi',
'lipidparticle':'In Lipid Particle',
'nucleus':'In Nucleus',
'bud':'At Bud',
'interactorsms':'Interactors by Mass Spec',
'interactorsyeast':'Interactors by Yeast Two-Hybrid',
'disorder':'Percent Disorder (DISOPRED2)',
'essential':'Essential Gene',
'halflife':'Protein Half-Life',
'absolutecost':'Absolute Cost',
'evolutionaryrate':'Evolutionary Rate',
'multifunctional':'Rank of Multifunctionality',
'percentala':'% Alanine',
'percentarg':'% Arginine',
'percentasn':'% Asparagine',
'percentasp':'% Aspartic Acid',
'percentcys':'% Cysteine',
'percentgln':'% Glutamine',
'percentglu':'% Glutamic Acid',
'percentgly':'% Glycine',
'percenthis':'% Histidine',
'percentile':'% Isoleucine',
'percentleu':'% Leucine',
'percentlys':'% Lysine',
'percentmet':'% Methionine',
'percentphe':'% Phenylalanine',
'percentpro':'% Proline',
'percentser':'% Serine',
'percentthr':'% Threonine',
'percenttrp':'% Tryptophan',
'percenttyr':'% Tyrosine',
'percentval':'% Valine',
'weissmanprion':'Prion-Like (Weissman)',
'tango':'Aggregation-Prone (TANGO)',
'gersteinprion':'Prion-Like (Gerstein)',
'lindquistprion':'Prion-Like (Lindquist)',
'iupredlong':'% Long-Stretch Disorder (IUPRED)',
'iupredshort':'% Short-Stretch Disorder (IUPRED)',
'disobindinglong':'% Long Disordered Binding (ANCHOR)',
'disobindingshort':'% Short Disordered Binding (ANCHOR)',
'percentiupredlongbinding':'% Long Disorder in Binding (ANCHOR)',
'percentiupredshortbinding':'% Short Disorder in Binding (ANCHOR)',
'scansitemotifs':'Scansite Motifs',
'percentscansitemotifs':'Scansite Motifs/Length',
'hubtype':'Protein Hub Type',
'openbiosystem.tap':'Open Biosystems TAP Plate Location'
}

#---- Views ----#
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/cite')
def cite():
	return render_template('cite.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		sender = request.form['sender']
		body = request.form['comment']
		#sender = request.args.get('sender', None)
		#body = request.args.get('comment', None)
		subject = 'CARPY feedback'
		recipient = 'jwinget@gmail.com'
		send_email(sender, recipient, subject, body)
		return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/protein/<id>')
def single(id):
	result = protein_query(id)
	if not result:
		return render_template('notfound.html')
	else:
		return render_template('single.html', result=result)

@app.route('/retrieve', methods=['GET','POST'])
def retrieve():
	if request.method == 'POST':
		ids = request.form['identifiers'].split()
		if len(ids) == 1:
			id = ids[0]
			return redirect(url_for('single', id=id))
		else:
			d = str(uuid.uuid1())
			os.mkdir('queries/'+d)
			f = open('queries/'+d+'/ids.txt', 'w')
			n = open('queries/'+d+'/not_found.txt', 'w')
			for i in ids:
				r = protein_query(i)
				if r:
					sys_name = r['systematicname']
					f.write(sys_name+'\n')
				else:
					n.write(i+'\n')
			f.close()
			return redirect(url_for('query', d=d))
	else:
		return render_template('searchform.html')

@app.route('/query/<d>')
def query(d):
	query_dir = 'queries/'+d+'/'
	f = open(query_dir+'ids.txt', 'r')
	ids = f.read().splitlines()
	
	# Collect unidentified ids
	n = open('queries/'+d+'/not_found.txt', 'r')
	not_found = n.read().splitlines()
	n.close()

	# Run the R script to determine enriched properties
	if not os.path.exists(query_dir+'enrichement_test.out'): # Only run if it hasn't been done
		outfile = query_dir+'enrichment_test.out'
		subprocess.call(['Rscript', 'scripts/enrichment_test.R', query_dir])

	# Process enrichment data
	enriched_dict = {}
	deenriched_dict = {}
	qe = open(query_dir+'quant_enrichment.csv', 'r')
	quant_enrichment = csv.reader(qe)
	for row in quant_enrichment:
		if row[0] != '':
			if float(row[1]) < 0.05:
				if float(row[2]) > 0:
					enriched_dict[row[0]] = [float(row[1]), float(row[2]), '+']
				else:
					deenriched_dict[row[0]] = [float(row[1]), float(row[2]), '']
	qe.close()
	ce = open(query_dir+'cat_enrichment.csv', 'r')
	cat_enrichment = csv.reader(ce)
	for row in cat_enrichment:
		if row[0] != '':
			if float(row[1]) < 0.05:
				if float(row[2]) > 1:
					enriched_dict[row[0]] = [float(row[1]), float(row[2]), 'x']
				else:
					deenriched_dict[row[0]] = [float(row[1]), float(row[2]), 'x']
	ce.close()

	# Display proteins
	result = [] 
	for i in ids:
		q = protein_query(i)
		result.append(q)
	return render_template('retrieve.html', not_found=not_found, result=result, enriched=enriched_dict, deenriched=deenriched_dict, name_dict=name_dict)
	f.close()

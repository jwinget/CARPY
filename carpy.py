from flask import Flask, render_template, request, redirect, url_for
from mongokit import Connection, Document
import uuid
import os
import subprocess

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
	# Run the R script to determine enriched properties
	outfile = query_dir+'enrichment_test.out'
	subprocess.call(['Rscript', 'scripts/enrichment_test.R', query_dir])
	n = open('queries/'+d+'/not_found.txt', 'r')
	not_found = n.read().splitlines()
	n.close()
	result = [] 
	for i in ids:
		q = protein_query(i)
		result.append(q)
	return render_template('retrieve.html', not_found=not_found, result=result)
	f.close()

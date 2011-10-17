from flask import Flask, render_template
from mongokit import Connection, Document

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

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object(__name__)

app.debug = True

# Mongo connection
connection = Connection(app.config['MONGODB_HOST'],
						app.config['MONGODB_PORT'])

#---- Models ----#
class Protein(Document):
	''' A class defining the protein properties '''
	structure = {
		'yorf': unicode,
		'genename': unicode,
		'sgid': unicode,
		'molecularweight': int,
		'pi': float,
		'cai': float,
		'proteinlength': int,
		'codonbias': int,
		'fopscore': float,
		'gravyscore': float,
		'aromaticityscore': float,
		'genetype': unicode,
		'orfid': int,
		'abundance': int,
		'localization': unicode,
		'localization_detailed': {
			'ambiguous': bool,
			'mitochondrion': bool,
			'vacuole': bool,
			'spindlepole': bool,
			'cellperiphery': bool,
			'punctatecomposite': bool,
			'vacuolarmembrane': bool,
			'er': bool,
			'nuclearperiphery': bool,
			'endosome': bool,
			'budneck': bool,
			'microtubule': bool,
			'golgi': bool,
			'lategolgi': bool,
			'peroxisome': bool,
			'actin': bool,
			'nucleolus': bool,
			'cytoplasm': bool,
			'ertogolgi': bool,
			'earlygolgi': bool,
			'lipidparticle': bool,
			'nucleus': bool,
			'bud': bool
			},
		'interactors': {
			'ms': int,
			'yeast2hybrid': int,
			'scansitemotifs': int,
			'percentscansitemotifs': float,
			'hubtype': unicode
			},
		'disorder': {
			'disorder': float,
			'iupredlong': float,
			'iupredshort': float,
			'disobindinglong': float,
			'disobindingshort': float
			},
		'essential': bool,
		'halflife': int,
		'absolutecost': float,
		'evolutionaryrate': float,
		'aa_percs': {
			'ala': float,
			'arg': float,
			'asn': float,
			'asp': float,
			'cys': float,
			'gln': float,
			'glu': float,
			'gly': float,
			'his': float,
			'ile': float,
			'leu': float,
			'lys': float,
			'met': float,
			'phe': float,
			'pro': float,
			'ser': float,
			'thr': float,
			'trp': float,
			'tyr': float,
			'val': float
			},
		'prion': {
			'weissman': bool,
			'tango': bool,
			'gerstein': bool,
			'lindquist': bool
			}
	}
	use_dot_notation = True
	required_fields = ['sgid']

# Register the Protein document with our current connection
connection.register([Protein])

#--- Views ----#
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/cite')
def cite():
	return render_template('cite.html')

@app.route('/retrieve')
def retrieve():
	return render_template('retrieve.html')

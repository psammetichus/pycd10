import lxml.etree as ET
import csv
import codecs

class DxNet (object):
	def __init__(self):
		self.dx = list()
		self.descIx = dict()
		self.codeIx = dict()
	def newDiagnosis(self, code, desc, **kwargs):
		n = Diagnosis(self, code, desc, **kwargs)
		self.dx.append(n)

		words = n.desc.split(" ")
		for word in words:
			if word.lower() in ["the", "a", "of", "an", "for"]:
				continue
			if word.lower() in self.descIx:
				self.descIx[word.lower()].add(n)
			else:
				self.descIx[word.lower()] = {n}

		if n.code in self.codeIx:
			self.codeIx[n.code].add(n)
		else:
			self.codeIx[n.code] = {n}

	def find_dx_by_keyword(self, *list_of_keywords):
		s = set()
		for word in list_of_keywords:
			if word in self.descIx:
				s = s.union(self.descIx[word])
		return list(s)

	def find_dx_by_code(self, code):
		return list(self.codeIx.get(code, list()))

	def find_dx_by_fuzzy_code(self, codeFrag):
		pass
		#would require a trie of the codes

	def store_to_csv(self, filename):
		with open(filename, 'wb') as f:
			wr = csv.writer(f)
			for dxn in self.dx:
				wr.writerow( map(encodeStr,
								(dxn.code,
								dxn.desc,
								dxn.excl1,
								dxn.excl2,
								dxn.incl,
								dxn.codealso,
								dxn.useaddl)))



def encodeStr(obj):
	if obj is not None:
		return codecs.utf_8_encode(obj)[0]
	else:
		return None



class Diagnosis (object):
	def __init__(self, dxnet, code, desc, incl=None, excl1=None, excl2=None,
			codealso=None, useaddl=None, terminal=False, kids=None):
		self.dxnet = dxnet
		self.code = code
		self.desc = desc
		self.incl = incl
		self.excl1 = excl1
		self.excl2 = excl2
		self.codealso = codealso
		self.useaddl = useaddl
		self.kids = kids
	def __repr__(self):
		return "<DX:%s |%s| >" % (self.code.ljust(9), self.desc[:50])
	def isbillable(self):
		return True if len(self.kids) > 0 else False


def getDxs(fileName):
	net = DxNet()
	rt = ET.parse(fileName).getroot()
	dxnodes = rt.findall('.//diag') #this finds all nodes, including non-billable ones
	#dxnodes = rt.xpath('//diag[not(descendant::diag)]')

	for dx in dxnodes:
		code = None
		desc = None
		others = dict()
		notes = dx.getchildren()
		for note in notes:
			if note.tag == 'name':
				code = note.text
			elif note.tag == 'desc':
				desc = note.text
			elif note.tag == 'inclusionTerm':
				others['incl'] = note.getchildren()[0].text
			elif note.tag == 'useAdditionalCode':
				others['useaddl'] = note.getchildren()[0].text
			elif note.tag == 'excludes1':
				others['excl1'] = note.getchildren()[0].text
			elif note.tag == 'excludes2':
				others['excl2'] = note.getchildren()[0].text
			elif note.tag == 'codeAlso':
				others['codealso'] = note.getchildren()[0].text
		if (code is None or desc is None):
			continue
		subdxs = dx.findall('./diag')
		if subdxs is []:
			others['kids'] = []
		else:
			others['kids'] = [subdx[0].text for subdx in subdxs]
		net.newDiagnosis(code, desc, **others)
	return net

#net = getDxs("FY15_Tabular.xml")


def sqlSave(dxnet, sqldb):
	pass
	

import loveICD10 as icdx

class EntryList (object):
    def __init__(self):
        self.entries = list()
        self.combos = dict()
        self.index = dict()

    def gulpEntries(self, fileName):
        with open(fileName, 'r') as f:
            for line in f.readlines():
                e = Entry(self, line)
                self.entries.append(e)
                if e.hasCombo():
                    if e.code9 in self.combos:
                        if e.scenario in self.combos[e.code9]:
                            self.combos[e.code9][e.scenario].append(e)
                        else:
                            self.combos[e.code9][e.scenario] = [e]
                    else:
                        self.combos[e.code9] = {e.scenario : [e]}
        self.indexEntries()
        for code, entries in self.combos.items():
            for entry in entries:
                for ientry in self.index[code]:
                    ientry.link(entry)


    def indexEntries(self):
        for e in self.entries:
            if e.code9 not in self.index:
                self.index[e.code9] = [e]
            else:
                self.index[e.code9].append(e)

    def map9code(self, code9):
        try:
            entries = self.index[code9]
            return [icdx.net.find_dx_by_code(i.codeX)[0] for i in entries]
        except (IndexError, KeyError):
            return []




class Entry (object):
    approx = False
    nomap = False
    combo = False
    scenario = None
    choice = None
    def __init__(self, entryList, entryLine):
        self.elist = entryList
        nine, ten, flags = [col for col in entryLine.split(" ") if len(col) > 0]

        self.parseFlags(flags)
        self.code9 = fmtICD9(nine)
        self.codeX = fmtICD10(ten) if not self.nomap else None
        self.links = list()

        if self.combo:
            self.scenario = int(flags[3])
            self.choice = int(flags[4])

    def parseFlags(self, flags):
        if flags[0] == '1':
            self.approx = True
        if flags[1] == '1':
            self.nomap = True
        if flags[2] == '1':
            self.combo = True

    def isExact(self):
        return not self.approx

    def has10code(self):
        return not self.nomap

    def hasCombo(self):
        return self.combo

    def __repr__(self):
        return "<Entry:: %s  %s" % (self.code9, self.codeX)

    def link(self, linkEntry):
        self.links.append(linkEntry)

    def otherMappedCodes(self):
        ll = self.elist.index[self.code9]
        i = ll.index(self)
        return ll[0:i] + ll[i+1:]




def fmtICD9(str):
    n = 3
    if str[0] == 'E':
        n = 4
    if len(str) == n:
        return str
    return str[:n] + "." + str[n:]

def fmtICD10(str):
    if len(str) == 3:
        return str
    return str[:3] + "." + str[3:]


el = EntryList()
el.gulpEntries('2014_I9gem.txt')



def translateCodes(listcodes):
    dd = list()
    ok = False
    ff = listcodes
    leftover = list()
    for line in ff:
        line = line.rstrip()
        print(">> Code %s possible translations" % (line,))
        tt = el.map9code(line)
        if len(tt) == 0:
            print("Code %s appears not to be valid. Trying trick" % line)
            tt = el.map9code(line + '0')
            if len(tt) == 0: #still?
                print("Code %s not valid even with trick" % line)
                leftover.append(line)
                continue

        if len(tt) == 1:
            print("Only one translation for code %s. Continuing." % line)
            dd.append( (line, tt[0]) )
            continue

        ok = False
        while ok is False:
            for i, t in enumerate(tt):
                print("\t\t%i.\t%s" % (i,t))
            print(">> Which code?")
            answer = int(input(">> ").rstrip())
            if answer >= len(tt) or answer < 0:
                print(">> Note a valid entry.")
            else:
                ok = True
            dd.append( (line, tt[answer]) )
    return dd, leftover

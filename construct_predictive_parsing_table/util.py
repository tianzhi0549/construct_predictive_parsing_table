class Symbol:
    def __init__(self, name):
        self.name=name
        self.first=set()
        self.follow=set()
        self.nullable=False

    def __str__(self):
        return self.name
    def set2Str(set):
        strSet=""
        for s in set:
            strSet+=str(s)+", "
        if(len(strSet)>0):
            strSet=strSet[:-2]
        return "set("+strSet+")"
    def dump(self):
        return "{{\n\tname: {0}\n\tnullable: {1}, \n\tFIRST: {2}, \n\tFOLLOW: {3}\n}}". \
                    format(self.name, self.nullable, 
                           Symbol.set2Str(self.first), 
                           Symbol.set2Str(self.follow))

class Terminal(Symbol):
    def __init__(self, name):
        super().__init__(name)
        self.first=set([self])

class NonTerminal(Symbol):
    def __init__(self, name):
        super().__init__(name)

class Production:
    def __init__(self, left, rightList):
        self.left=left
        self.rightList=rightList
    def __str__(self):
        str=""
        for symbol in self.rightList:
            str+=symbol.name+" ";
        str=str[:-1]
        return "{0}->{1}".format(self.left.name, str)
    def __eq__(self, p):
        if self.left!=p.left: return False
        if len(self.rightList)!=len(p.rightList): return False
        for s1, s2 in zip(self.rightList, p.rightList):
            if s1!=s2:
                return False
        return True
    def __hash__(self):
        r=0
        for s in self.rightList:
            r+=hash(s)
        return r+hash(self.left)


def ComputeNullable(productions):
    while True:
        hasModification=False
        for p in productions:
            for symbol in p.rightList:
                if symbol.nullable==False:
                    break
            else:
                if not p.left.nullable:
                    p.left.nullable=True
                    hasModification=True
        if not hasModification:
            break

def ComputeFirstSet(productions):
    while True:
        hasModification=False
        for p in productions:
            size=len(p.rightList)
            i=0
            while i<size:
                firstSize=len(p.left.first)
                p.left.first|=p.rightList[i].first
                if len(p.left.first)!=firstSize:
                    hasModification=True
                if p.rightList[i].nullable:
                    i+=1
                else:
                    break
        if not hasModification:
            break

def ComputeFollowSet(productions):
    while True:
        hasModification=False
        for p in productions:
            size=len(p.rightList)
            i=size-1
            while i>=0:
                followSize=len(p.rightList[i].follow)
                if i==size-1:
                    p.rightList[i].follow|=p.left.follow
                else:
                    p.rightList[i].follow|=p.rightList[i+1].first
                    if p.rightList[i+1].nullable:
                        p.rightList[i].follow|=p.rightList[i+1].follow
                if len(p.rightList[i].follow)!=followSize:
                    hasModification=True
                i-=1

        if not hasModification:
            break

def ComputeSequenceFirstSet(symbols):
    firstSet=set()
    size=len(symbols)
    i=0
    while i<size:
        firstSet|=symbols[i].first
        if symbols[i].nullable:
            i+=1
        else:
            break
    return firstSet

def isNullable(symbols):
    for s in symbols:
        if s.nullable==False:
            return False
    return True

def LoadRules(fileName):
    fp=open(fileName)
    nonterminals=[]
    terminals=[]
    productions=[]
    usedName={}
    for l in fp:
        if l=="": continue
        arr=l.split("->")
        leftStr=arr[0].strip()
        if leftStr not in usedName:
            name=NonTerminal(leftStr)
            nonterminals.append(name)
            usedName[leftStr]=name
        else:
            name=usedName[leftStr]
        rightList=[]
        rightStr=arr[1].strip()
        if rightStr!="":
            arr=rightStr.split(" ")
            for symbolName in arr:
                symbolName=symbolName.strip()
                if symbolName[0]=="$":
                    symbolName=symbolName[1:]
                    if symbolName not in usedName:
                        symbol=Terminal(symbolName)
                        terminals.append(symbol)
                        usedName[symbolName]=symbol
                    else:
                        symbol=usedName[symbolName]
                else:
                    if symbolName not in usedName:
                        symbol=NonTerminal(symbolName)
                        nonterminals.append(symbol)
                        usedName[symbolName]=symbol
                    else:
                        symbol=usedName[symbolName]
                rightList.append(symbol)
        productions.append(Production(name, rightList))
    fp.close()
    return nonterminals, terminals, productions

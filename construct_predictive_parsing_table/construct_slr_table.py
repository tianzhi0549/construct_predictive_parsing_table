#coding=gbk
from util import *
class Item:
    DOT="·"
    def __init__(self, production, dotPos):
        if dotPos>len(production.rightList):
            raise IndexError("dotPos out of range")
        self.production=production
        self.dotPos=dotPos

    def getSymbolAfterDot(self):
        if self.dotPos>=len(self.production.rightList):
            return None
        else:
            return self.production.rightList[self.dotPos]

    def advanced(self):
        return Item(self.production, self.dotPos+1)

    def __eq__(self, other):
        if other.production==self.production and \
                other.dotPos==self.dotPos:
            return True
        return False
    def __hash__(self):
        return hash(self.dotPos)+hash(self.production)

    def __str__(self):
        rightStr=""
        if self.dotPos==0:
            rightStr+=Item.DOT
        for i, s in enumerate(self.production.rightList):
            rightStr+=str(s)
            if i+1==self.dotPos:
                rightStr+=Item.DOT
        return str(self.production.left)+"->"+rightStr

    def isAcc(self):
        return self.dotPos==len(self.production.rightList)

class ItemSet(set):
    def __init__(self, productionList, iterable=[]):
        super().__init__(iterable)
        self.productionList=productionList

    def closure(self):
        closureSet=ItemSet(self.productionList, self)
        while True:
            hasModified=False
            for item in closureSet:
                symbol=item.getSymbolAfterDot()
                if symbol!=None:
                    subSet=set(self.productionList.getSubListByLeft(symbol))
                    size=len(closureSet)
                    closureSet|=set([Item(p, 0) for p in subSet])
                    if len(closureSet)!=size:
                        hasModified=True
                        break
            if not hasModified:
                break
        return closureSet
    def goTo(self, symbol):
        rSet=ItemSet(self.productionList)
        for item in self:
            if item.getSymbolAfterDot()==symbol:
                rSet.add(item.advanced())
        return rSet.closure()

    def __str__(self):
        r=""
        for item in self:
            r+=str(item)+"\n"
        return r

    def __eq__(self, other):
        if len(self)!=len(other):
            return False
        for item1, item2 in zip(self, other):
            if item1!=item2:
                return False
        return True

class State:
    def __init__(self, itemSet):
        self.itemSet=ItemSet(itemSet.productionList, itemSet)
        self.transform={}
        self.num=0

    def __eq__(self, other):
        return self.itemSet==other.itemSet
    def __hash__(self):
        return hash(str(self.itemSet))

    def __str__(self):
        r=str(self.num)+"\n"
        r+="\t"+str(self.itemSet).replace("\n", "\n\t")
        r+="TRANSFORM: "
        for symbol, state in self.transform.items():
            r+=str(symbol)+":"+str(state.num)+" "
        return r

    def addtransform(self, symbol, state):
        if symbol not in self.transform:
            self.transform[symbol]=state
        else:
            raise BaseException("文法错误")

class StateSet(set):
    def __init__(self, iterable=[]):
        super().__init__(iterable)
        self.num=len(self)

    def add(self, state):
        state.num=self.num
        super().add(state)
        self.num+=1

    def __str__(self):
        r=""
        for state in self:
            r+=str(state)+"\n"
        return r

def ComputeStateSet(initState, stateSet, symbols):
    for symbol in symbols:
        itemSet=initState.itemSet.goTo(symbol)
        if len(itemSet)!=0:
            state=State(itemSet)
            if state not in stateSet:
                stateSet.add(state)
                ComputeStateSet(state, stateSet, symbols)
            else:
                for s in stateSet:
                    if s==state:
                        state=s

            initState.addtransform(symbol, state)

def ConstructSLRTable(stateSet):
    table=[{"ACTION":{}, "GOTO": {}} for i in range(len(stateSet))]
    for state in stateSet:
        for symbol in state.transform:
            if isinstance(symbol, Terminal):
                table[state.num]["ACTION"][str(symbol)]="s"+str(state.transform[symbol].num)
            else:
                table[state.num]["GOTO"][str(symbol)]=str(state.transform[symbol].num)
        for item in state.itemSet:
            if item.isAcc():
                for symbol in item.production.left.follow:
                    if str(symbol) in table[state.num]["ACTION"]:
                        table[state.num]["ACTION"][str(symbol)]+=" "+str(item.production)
                        print("Conflict: {0} {1}".format(state.num, symbol))
                    else:
                        table[state.num]["ACTION"][str(symbol)]=str(item.production)
    return table

def Table2JSON(table):
    '''
        [
            {
                "ACTION": {
                    tokenType: "s0",
                    tokenType: "E->E+T"
                },
                "GOTO": {
                    tokenType: "0"
                }
            },

        ]
    '''
    import json
    return json.dumps(table, indent=4)
    

def PrintTable(table):
    for stateNum, row in enumerate(table):
        print("{0}:".format(stateNum))
        for attr in row:
            if len(row[attr])==0:
                continue
            print("\t{0}:".format(attr))
            for symbol in row[attr]:
                print("\t\t{0}:{1}".format(symbol, row[attr][symbol]))
        print("\n")

nonterminals, terminals, productions=LoadRules("cminus.txt")
tokenEOF=Terminal('EOF')
terminals.append(tokenEOF)
productions[0].left.follow.add(tokenEOF)
ComputeNullable(productions)
ComputeFirstSet(productions)
ComputeFollowSet(productions)
startSymbol=productions[0].left
initState=State(ItemSet(productions, [Item(productions[0], 0)]).closure())
stateSet=StateSet([initState])
ComputeStateSet(initState, stateSet, nonterminals+terminals)
print(Table2JSON(ConstructSLRTable(stateSet)))

from util import *
def PrintTable(table):
    for nonterminal in table:
        print("{0}:".format(nonterminal))
        for terminal in table[nonterminal]:
            if len(table[nonterminal][terminal])==0:
                continue
            print("\t{0}:".format(terminal))
            for p in table[nonterminal][terminal]:
                print("\t\t{0}".format(p))

def ComputeTable(nonterminals, terminals, productions):
    ComputeNullable(productions)
    ComputeFirstSet(productions)
    ComputeFollowSet(productions)
    table={}
    for nonterminal in nonterminals:
        table[nonterminal]={}
        for terminal in terminals:
            table[nonterminal][terminal]=[]
            for p in productions:
                if p.left==nonterminal:
                    if terminal in ComputeSequenceFirstSet(p.rightList):
                        if p not in table[nonterminal][terminal]:
                            table[nonterminal][terminal].append(p)
                    if isNullable(p.rightList):
                        if terminal in p.left.follow:
                            if p not in table[nonterminal][terminal]:
                                table[nonterminal][terminal].append(p)
    return table

if __name__=="__main__":
    nonterminals, terminals, productions=LoadRules("cminus-grammer-rules.txt")
    PrintTable(ComputeTable(nonterminals, terminals, productions))

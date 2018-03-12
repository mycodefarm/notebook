class _TreeNode:
    '''定义FP树'''

    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


class JFPGrowth(object):
    def __init__(self, dataSet, minSupport=0.1, minConfidence=0.6):
        self.__dataSet = self.__createInitSet(dataSet)
        self.minSup = int(minSupport * len(self.__dataSet)) + 1
        self.minConf = minConfidence
        self.__freqItems = {}
        self.__rules = []

    def __createInitSet(self, dataSet):
        retDict = {}
        for trans in dataSet:
            retDict[frozenset(trans)] = 1
        return retDict

    def __createTree(self, dataSet):
        '''
        构建FP树
        '''
        headerTable = {}
        for trans in dataSet:
            for item in trans:
                headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
        # 去除不满足最小支持度的项
        for k in list(headerTable.keys()):
            if headerTable[k] < self.minSup:
                del (headerTable[k])
        freqItemSet = set(headerTable.keys())
        if len(freqItemSet) == 0: return None, None
        for k in headerTable:
            headerTable[k] = [headerTable[k], None]
        retTree = _TreeNode('Null Set', 1, None)
        for tranSet, count in dataSet.items():
            localD = {}
            for item in tranSet:
                if item in freqItemSet:
                    localD[item] = headerTable[item][0]
            if len(localD) > 0:
                # 按频率降序排列
                orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
                self.__updateTree(orderedItems, retTree, headerTable, count)
        return retTree, headerTable

    def __updateTree(self, items, inTree, headerTable, count):
        if items[0] in inTree.children:
            inTree.children[items[0]].inc(count)
        else:
            inTree.children[items[0]] = _TreeNode(items[0], count, inTree)
            if headerTable[items[0]][1] == None:
                headerTable[items[0]][1] = inTree.children[items[0]]
            else:
                self.__updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
        if len(items) > 1:
            self.__updateTree(items[1::], inTree.children[items[0]], headerTable, count)

    def __updateHeader(self, nodeToTest, targetNode):
        while nodeToTest.nodeLink != None:
            nodeToTest = nodeToTest.nodeLink
        nodeToTest.nodeLink = targetNode

    def __ascendTree(self, leafNode, prefixPath):
        '''
        寻找条件模式基
        '''
        if leafNode.parent != None:
            prefixPath.append(leafNode.name)
            self.__ascendTree(leafNode.parent, prefixPath)

    def __findPrefixPath(self, basePat, treeNode):
        condPats = {}
        while treeNode != None:
            prefixPath = []
            self.__ascendTree(treeNode, prefixPath)
            if len(prefixPath) > 1:
                condPats[frozenset(prefixPath[1:])] = treeNode.count
            treeNode = treeNode.nodeLink
        return condPats

    def __mineTree(self, inTree, headerTable, preFix):
        '''
        创建条件FP树
        '''
        bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]
        for basePat in bigL:
            newFreqSet = preFix.copy()
            newFreqSet.add(basePat)
            support = headerTable[basePat][0]
            self.__freqItems[frozenset(newFreqSet)] = support
            condPattBases = self.__findPrefixPath(basePat, headerTable[basePat][1])
            myCondTree, myHead = self.__createTree(condPattBases)

            if myHead != None:
                # debug
                # print('条件树:', newFreqSet)
                # myCondTree.disp(1)
                self.__mineTree(myCondTree, myHead, newFreqSet)

    def __ruleGenerator(self):
        '''
        挖掘关联规则
        '''
        for freqItemSet in self.__freqItems:
            if len(freqItemSet) > 1:
                self.__getRules(freqItemSet, freqItemSet)

    def __removeStr(self, set, str):
        tempSet = []
        for elem in set:
            if (elem != str):
                tempSet.append(elem)
        tempFrozenSet = frozenset(tempSet)
        return tempFrozenSet

    def __getRules(self, freqItemSet, currSet):
        for freqElem in currSet:
            subSet = self.__removeStr(currSet, freqElem)
            try:
                confidence = self.__freqItems.get(freqItemSet, 1) / self.__freqItems.get(subSet, 10)
            except:
                confidence = 0.1
            if confidence >= self.minConf:
                flag = False
                for rule in self.__rules:
                    if rule[0] == subSet and rule[1] == freqItemSet - subSet:
                        flag = True
                if flag == False:
                    self.__rules.append((subSet, freqItemSet - subSet, confidence))
                if len(subSet) >= 2:
                    self.__getRules(freqItemSet, subSet)

    def getFreqItems(self):
        if len(self.__freqItems) > 0:
            return self.__freqItems
        tree, header = self.__createTree(self.__dataSet)
        self.__mineTree(tree, header, set([]))
        return self.__freqItems

    def getFinalRules(self):
        # 如果没有生成频繁集先要生成
        if len(self.__freqItems) == 0:
            self.getFreqItems()
        self.__ruleGenerator()
        return self.__rules

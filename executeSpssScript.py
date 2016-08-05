#-*-coding: utf-8-*-
import re
import csv
import os
import sys
import SpssClient as sc

## rootDir may relative path or absolute path
## output is file list with absolute path
def getFilesInDir(rootDir):
    if not os.path.isabs(rootDir):
        rootAbsDir = os.path.abspath(rootDir)
    else:
        rootAbsDir = rootDir
    print rootAbsDir
    fileList = []
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            fileList.append(os.path.join(rootAbsDir, f))
    return fileList

def getRotatedMatrix(pivotTable, rowCount, colCount):
    columnLabels = pivotTable.ColumnLabelArray()
    rowLabels = pivotTable.RowLabelArray()
    dataArray = pivotTable.DataCellArray()
    table = []

    for i in range(0, rowCount):
        row = []
        for j in range(0, colCount):
            if i == 0:
                if j == 0:
                    row.append('')
                else:
                    row.append(columnLabels.GetValueAt(1, j -1))  
            else:
                if j == 0:
                    # print "i = %r" %i 
                    if i < rowCount:
                        row.append(rowLabels.GetValueAt(i-1, 1)) 
                else:
                    row.append(dataArray.GetValueAt(i-1, j-1))
        table.append(row)

    print "table is %r" %table
    return table


## **
## sFile is absolute path
## outDir is absolute path
def execute(sFile, outDir):
    
    fNames = os.path.split(sFile)
    initName = fNames[1].split('.')[0]

    reportFile = initName + '_report.spv'
    print 'reportFile is %r' %reportFile
    reportFile = os.path.join(outDir, reportFile)
    resultFile = initName + '_result.csv'
    resultFile = os.path.join(outDir, resultFile)

    htmlFile = initName + "_report.html"
    htmlFile = os.path.join(outDir, htmlFile)

    htmlTemplate = "html_template.html"
    
    try:
        sc.StartClient()
        print("begin to execute synx...")
        print ("begin to get data from %s "%sFile)
        sc.RunSyntax(r"""
        GET DATA  /TYPE=TXT
          /FILE="%s"
          /ENCODING='UTF8'
          /DELCASE=LINE
          /DELIMITERS=","
          /ARRANGEMENT=DELIMITED
          /FIRSTCASE=2
          /IMPORTCASE=ALL
          /VARIABLES=
          province A200
          rptn F4.0
          rptm F2.0
          corpId F5.0
          corpName A43
          C1 F8.4
          C2 F8.4
          C3 F8.4
          C4 F10.4
          C5 F8.4
          C6 F8.4
          C7 F7.4
          C8 F7.4
          C9 F7.4
          C10 F7.4
          C11 F7.4
          C9_avg F7.4
          C10_avg F7.4
          C11_avg F7.4.
        CACHE.
        EXECUTE.
        DATASET NAME dataset1 WINDOW=FRONT.

        DATASET ACTIVATE dataset1.
        COMPUTE t1=1/C1.
        EXECUTE.
        COMPUTE t7=1-C7.
        EXECUTE.
        COMPUTE t8=1-C8.
        EXECUTE.
        COMPUTE t9=1/abs(C9_avg-C9).
        EXECUTE.
        COMPUTE t10=1/abs(C10_avg-C10).
        EXECUTE.
        COMPUTE t11=1/abs(C11_avg-C11).
        EXECUTE.

        FACTOR
          /VARIABLES t1 C2 C3 C4 C5 C6 t7 t8 t9 t10 t11
          /MISSING LISTWISE 
          /ANALYSIS t1 C2 C3 C4 C5 C6 t7 t8 t9 t10 t11
          /PRINT INITIAL CORRELATION KMO EXTRACTION ROTATION FSCORE
          /FORMAT BLANK(.10)
          /PLOT EIGEN ROTATION
          /CRITERIA FACTORS(6) ITERATE(25)
          /EXTRACTION PC
          /CRITERIA ITERATE(25)
          /ROTATION VARIMAX
          /SAVE REG(ALL)
          /METHOD=CORRELATION.


        OUTPUT SAVE NAME=Document1
        OUTFILE='%s'
        LOCK=NO.

        SAVE TRANSLATE OUTFILE='%s'
          /TYPE=CSV
          /ENCODING='UTF8'
          /MAP
          /REPLACE
          /FIELDNAMES
          /CELLS=VALUES.

        """ %(sFile, reportFile, resultFile))

        print("exec synx complete !")

        # can't save to csv file
        #activeDataDoc = sc.GetActiveDataDoc()
        #activeDataDoc.SaveAs('d:/tmp/0801/new_dataSet.csv')

        ### get pivot table number
        outDoc = sc.GetDesignatedOutputDoc()
        outputItems = outDoc.GetOutputItems()

        for i in range(outputItems.Size()-1, -1, -1):
            outputItem = outputItems.GetItemAt(i)
            if outputItem.GetType() == sc.OutputItemType.PIVOT \
               and outputItem.GetDescription() == 'Total Variance Explained':
                break

        pivotTable = outputItem.GetSpecificType()
        print('get result from pivotTable: ' + pivotTable.GetTitleText())

        rowLabels = pivotTable.RowLabelArray()
        columnLabels = pivotTable.ColumnLabelArray()
        dataArray = pivotTable.DataCellArray()

        weight_facts = []
        for i in range(6):
            weight_facts.append(float(dataArray.GetValueAt(i, 7)))
        weight_sum = float(dataArray.GetValueAt(5, 8))

        print("each weight[0-5, 7] : ", weight_facts)
        print("sum: [5,8]", weight_sum)

        ## caculate result of score number 
        filename = resultFile
        req = re.compile(r'\t|,|:')

        data_file_name =filename
        returnMat = []

        i = 0
        with open(data_file_name) as fr:
            for line in fr.readlines():
                line = line.strip()
                listFromLine = req.split(line)
                if i == 0 :
                    listFromLine.append('score')
                    returnMat.append(listFromLine)
                    i = i + 1
                    continue
                else:
                    score = 0
                    try:
                        fact1 = float(listFromLine[25])
                        fact2 = float(listFromLine[26])
                        fact3 = float(listFromLine[27])
                        fact4 = float(listFromLine[28])
                        fact5 = float(listFromLine[29])
                        fact6 = float(listFromLine[30])
                        score = (fact1 * weight_facts[0] + fact2 * weight_facts[1] + fact3 * weight_facts[2] + \
                            fact4 * weight_facts[3] + fact5 * weight_facts[4] + fact6 * weight_facts[5])/weight_sum
                    except ValueError as e:
                        pass
                    listFromLine.append(score)
                    returnMat.append(listFromLine)
                i = i + 1
        #print(returnMat)

        def lastElem(l):
            return l[-1]

        returnMat.sort(key = lastElem, reverse = True)

        f = open(resultFile, "wb")
        w = csv.writer(f)
        w.writerows(returnMat)
        f.close()

        

        html = open(htmlFile, 'wb')


        for i in range(outputItems.Size()-1, -1, -1):
            outputItem = outputItems.GetItemAt(i)
            if outputItem.GetType() == sc.OutputItemType.PIVOT \
               and outputItem.GetDescription() == 'Rotated Component Matrix':
                break
        pivotTable = outputItem.GetSpecificType()

        print('get rotated component matrix from pivotTable: ' + pivotTable.GetTitleText())



        # for i in range(0, 6):
        #     print 'columnLabel: %s' %columnLabels.GetValueAt(1, i)

        
        # for i in range(0, 11):
        #     print 'rowLabel: %s' %rowLabels.GetValueAt(i, 1)
        
        table = getRotatedMatrix(pivotTable, 12, 7)
        
        table_html = ""
        table_html += r"""  
            <table border="1px" cellspacing="" cellpadding="">
            <caption >%s</caption>
        """%pivotTable.GetTitleText()

        for i in range(0, len(table)):
            table_html += "<tr>"
            row = table[i]
            for j in range(0, len(row)):
                table_html += ("<td>")
                table_html += (row[j])
                table_html += ("</td>")
            table_html += ("</tr>")
        table_html += "</table>"
        print "html: %s" %table_html


    finally:
        sc.StopClient()



#-*-coding: utf-8-*-
import re
import csv
import os
import sys
import SpssClient as sc
import contant

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

def getRotatedMatrix(pivotTable, rowLabels, rowCount, colCount):
    columnLabels = pivotTable.ColumnLabelArray()
    # rowLabels = pivotTable.RowLabelArray()
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
                        row.append(rowLabels[i-1]) 
                else:
                    row.append(dataArray.GetValueAt(i-1, j-1))
        table.append(row)
    return table

def convertMatrixToHtml(title, table, enable_color = False):
    table_html = u""
    table_html += u"""  
        <table class="gridtable">
        <h1 >%s</h1>
    """%unicode(title, 'utf-8')
    for i in range(0, len(table)):
        table_html += u"<tr>"
        row = table[i]
        for j in range(0, len(row)):
            
            # val = 0.0
            # if i > 0 and j == 0:
            #   if type(row[j]) is not unicode:
            #     val = unicode(str(row[j]), 'utf-8')
            #   else:
            #     val = row[j]
            # else:
            #   val = row[j]
            
            val = row[j]
            if i == 0 or j == 0:
              table_html += (u"<th>")
            else:
              try:
                val = float(val)
              except:
                pass
              if(type(val) is float):
                if(abs(float(val)) > 0.7 and enable_color):
                  table_html += u"<td bgcolor='aquamarine'>"
                else:
                  table_html += u"<td>"
              else:
                table_html += (u"<td>")
            if type(val) is not unicode:
              val = unicode(str(val), 'utf-8')
            table_html += val
            if i == 0 or j == 0:
                table_html += (u"</th>")
            else:
                table_html += (u"</td>")
        table_html += (u"</tr>")
    table_html += u"</table>"
    return table_html

def getPivotTable(outputItems, name):
  for i in range(outputItems.Size()-1, -1, -1):
      outputItem = outputItems.GetItemAt(i)
      if outputItem.GetType() == sc.OutputItemType.PIVOT \
         and outputItem.GetDescription() == name:
          break
  pivotTable = outputItem.GetSpecificType()
  return pivotTable


## **
## sFile is absolute path
## outDir is absolute path
def execute(sFile, outDir):
    
    fNames = os.path.split(sFile)
    initName = fNames[1].split('.')[0]

    reportFile = initName + '_report.spv'
    reportFile = os.path.join(outDir, 'report_files', reportFile)
    print 'reportFile is %r' %reportFile

    resultFile = initName + '_result.csv'
    resultFile = os.path.join(outDir, 'report_files', resultFile)

    report_dir = os.path.join(outDir, 'report_files')
    if not os.path.exists(report_dir):
      os.makedirs(report_dir)
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

        pivotTable = getPivotTable(outputItems, 'Total Variance Explained')

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

        ## read factor data from data_file
        print "data_file_name:  %r" %data_file_name
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


        area_id = initName.split('_')[1]
        area_name = contant.area_map[area_id]
   

        if area_name is None:
          area_name = initName

        htmlFile = area_name + r"_report.html"
        htmlFile = os.path.join(outDir, 'html', htmlFile)

        htmlDir =  os.path.join(outDir, 'html')
        if not os.path.exists(htmlDir):
          os.makedirs(htmlDir)
        # generate html files
        htmlF = open(htmlFile, 'w')

        html = u"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <title></title>
            <style type="text/css">
              table.gridtable {
                font-family: verdana, arial, sans-serif;
                font-size: 11px;
                color: #333333;
                border-width: 1px;
                border-color: #666666;
                border-collapse: collapse;
              }
              
              table.gridtable th {
                border-width: 1px;
                padding: 8px;
                border-style: solid;
                border-color: #666666;
                background-color: #dedede;
              }
              
              table.gridtable td {
                border-width: 1px;
                padding: 8px;
                border-style: solid;
                border-color: #666666;
              }     
            </style>
          </head>
        """

        html += u"<body>"
        # the top 20 
        table_html = convertMatrixToHtml('前20名典当行', returnMat[0:20])
        html += table_html

        # the last 20 
        # table_html = convertMatrixToHtml('后20名典当行', returnMat[-1:-21:-1])
        # html += table_html

        pivotTable = getPivotTable(outputItems, 'Rotated Component Matrix')

        row = 12
        column = 7

        rowLabels = [u'资产负债率', u'总资产增长率', u'典当资金周转率', u'总资产利润率', u'净资产增长率', u'净资产收益率', u'期末逾期贷款率', u'绝当率', u'单笔超注册资金25%贷款占比', u'房地产集中度', u'大额房地产余额占比']
        table = getRotatedMatrix(pivotTable, rowLabels, row, column)
        
        table_html = convertMatrixToHtml("旋转后的成分矩阵", table, True)
        html += table_html
        
        pivotTable = getPivotTable(outputItems, 'Total Variance Explained')  
        row = 12
        column = 10
        rowLabels = [u'组件1', u'组件2', u'组件3', u'组件4', u'组件5', u'组件6', u'组件7', u'组件8', u'组件9', u'组件10', u'组件11']
        table = getRotatedMatrix(pivotTable, rowLabels, row, column) 
        table_html = convertMatrixToHtml("总方差解释", table)
        html += table_html


         # all 
        table_html = convertMatrixToHtml('所有典当行排名', returnMat)
        html += table_html

        html += u"</body>"
        html += u"</html>"

        htmlF.write(html.encode('utf-8'))
        htmlF.close()

    finally:
        sc.StopClient()



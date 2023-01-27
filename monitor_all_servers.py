##############################################
# Weblogic Server WLST Script
# Author: Ahmed Aboulnaga
# Date:   2020-03-16
##############################################

import os
import sys

# Username and password
uname = 'weblogic'
pwd = 'welcome1'

# Get server name
parServerName = sys.argv[1]

# Connect to server
url = 't3://' + parServerName + ':7001'
connect(uname, pwd, url)

# Write output to HTML file
fo = open("/home/oracle/scripts/monitorstatus.html", "wb+")

#----------------------------------------
# Report Server Status
#----------------------------------------
fo.write('<div>')
fo.write('\n<h3>SERVER STATUS REPORT: ' + url + '</h3>\n\n')

def getRunningServerNames():
    domainConfig()
    return cmo.getServers()

serverNames = getRunningServerNames()
domainRuntime()

def healthstat(server_name):
    cd('/ServerRuntimes/' + server_name + '/ThreadPoolRuntime/ThreadPoolRuntime')
    s = get('HealthState')
    x = s.toString().split(',')[2].split(':')[1].split('HEALTH_')[1]
    return x

serverNames = domainRuntimeService.getServerRuntimes()
getRunningServerNames()
domainRuntime()

# Create table for Server Report Status
fo.write('<table style="font:normal 12px verdana, arial, helvetica, sans-serif; border:1px solid #1B2E5A;text-align:center" bgcolor="#D7DEEC" width="400" border="0">')
fo.write('<caption style="font-weight:bold; letter-spacing:10px; border:1px solid #1B2E5A">SERVER STATUS</caption>')
fo.write('<tr align="center" bgcolor="#5F86CF"><td>Server Name</td><td>Status</td><td>Health</td></tr>')

rowNum = 0;

for name in serverNames:
    status = str(name.getState())
    health = healthstat(name.getName())
    # Alternate Report Row Color
    if rowNum % 2 == 0:
        rowColor = '#D7DEEC'
    else:
        rowColor = '#F4F6FA'
    # Change cell color based on status returned
    hcolor = 'green'
    if health != 'OK':
        if health == 'WARN':
            hcolor = 'yellow'
        else:
            hcolor = 'red'
    else:
        hcolor = 'green'

    if status != 'RUNNING':
        if  status == 'WARNING':
            fo.write('<tr align="center" bgcolor=' + rowColor + '><td> ALERT!' + name.getName() + ' </td><td>' + status + '</td><td style="background-color:' + hcolor + ';font-weight:bold;">' + health + '</td></tr>')
        else:
            fo.write('<tr align="center" bgcolor=' + rowColor + '><td> ALERT!' + name.getName() + ' </td><td> ' + status + '  </td><td style="background-color:' + hcolor + ';font-weight:bold;">' + health + '</td></tr>')
    else:
        fo.write('<tr align="center" bgcolor=' + rowColor + '><td> ' + name.getName() + ' </td><td> ' + status + ' </td><td style="background-color:' + hcolor + ';"><b>' + health + ' </b></td></tr> ')

    rowNum += 1

fo.write("</table><br/><br/>")

#----------------------------------------
# Report Heap Details
#----------------------------------------

# Definition to print a running servers heap details
def printHeapDetails(server_name):
    domainRuntime()
    cd('/')
    cd('ServerRuntimes/' + server_name + '/JVMRuntime/' + server_name)
    hf = float(get('HeapFreeCurrent')) / 1024
    hs = float(get('HeapSizeCurrent')) / 1024
    hfpct = float(get('HeapFreePercent'))
    hf = round(hf / 1024, 2)
    hs = round(hs / 1024, 2)
    cellcolor = rowColor
    if hfpct <= 20 and server_name != 'AdminServer':
        if hfpct <= 10:
            cellcolor = 'red'
        else:
            cellcolor = 'yellow'
    else:
        cellcolor = rowColor

    fo.write('<tr bgcolor=' + cellcolor + ' align="center"><td align="left">' + server_name + '  </td><td>' + `hf` + 'MB  </td><td>' + `hs` + 'MB  </td><td>' + `hfpct` + '%  </td></tr>')

# Calling printHeapDetails with arguments
# Create Table for Heap Details
fo.write('<table style="font:normal 12px verdana, arial, helvetica, sans-serif; border:1px solid #1B2E5A" bgcolor="#D7DEEC" width="600" border="0">')
fo.write('<caption style="font-weight:bold; letter-spacing:10px; border:1px solid #1B2E5A">SERVER HEAP SIZE REPORT</caption>')
fo.write('<tr align="center" bgcolor="#5F86CF"><td> Managed Server</td><td>HeapFreeCurrent</td><td>HeapSizeCurrent</td><td>HeapFreePercent</td></tr>')
servers = domainRuntimeService.getServerRuntimes();
rowNum = 0;
for server in servers:
    # Alternate Report Row Color
    if rowNum % 2 == 0:
        rowColor = '#D7DEEC'
    else:
        rowColor = '#F4F6FA'
    printHeapDetails(server.getName())
    # Increment Row Color
    rowNum += 1

fo.write('</table><br /><br />')

#----------------------------------------
# Report JDBC Status
#----------------------------------------

fo.write('\n<h3>SERVER JDBC RUNTIME INFORMATION</h3>\n\n')
servers = domainRuntimeService.getServerRuntimes();
for server in servers:
    jdbcRuntime = server.getJDBCServiceRuntime();
    datasources = jdbcRuntime.getJDBCDataSourceRuntimeMBeans();
    # Create Table for JDBC Status
    fo.write('<table style="font:normal 12px verdana, arial, helvetica, sans-serif; border:1px solid #1B2E5A" bgcolor="#D7DEEC" width="600" border="0">')
    fo.write('<caption style="font-weight:bold; letter-spacing:10px; border:1px solid #1B2E5A">' + server.getName() + '</caption>')
    fo.write('<tr align="center" bgcolor="#5F86CF"><td> Data Source:</td><td>State</td><td>Active Connections</td><td>Waiting for Connections</td></tr>')
    rowNum = 0;
    for datasource in datasources:
        if rowNum % 2 == 0:
            rowColor = '#D7DEEC'
        else:
            rowColor = '#F4F6FA'

        if datasource.getState() != "Running":
            stateColor = "red"
        else:
            stateColor = rowColor
        if datasource.getActiveConnectionsCurrentCount() > 10:
            acColor = "yellow"
            if datasource.getActiveConnectionsCurrentCount() > 20:
                acColor = "red"
        else:
            acColor = rowColor
        if datasource.getWaitingForConnectionCurrentCount() > 2:
            wcColor = "yellow"
            if datasource.getWaitingForConnectionCurrentCount() > 5:
                wcColor = "red"
        else:
            wcColor = rowColor

        fo.write('<tr align="center" bgcolor=' + rowColor + '><td align="left">' + datasource.getName() + ' </td><td style="background-color:' + stateColor + '">' + datasource.getState() + ' </td><td  style="background-color:' + acColor + '" >' + repr(datasource.getActiveConnectionsCurrentCount()) + ' </td><td  style="background-color:' + wcColor + '" > ' + repr(datasource.getWaitingForConnectionCurrentCount()) + ' </td></tr>');
        rowNum += 1
    fo.write('</table><br /><br />')

#----------------------------------------
# Report JMS Status
#----------------------------------------

fo.write('\n<h3>SERVER JMS STATUS INFORMATION</h3>\n\n')
# Print JMS status for all servers
servers = domainRuntimeService.getServerRuntimes();

for server in servers:
    serverName = server.getName();
    jmsRuntime = server.getJMSRuntime();
    jmsServers = jmsRuntime.getJMSServers();
    if not jmsServers:
        fo.write('<h4>No JMS Information For ' + serverName + ' </h4> \n')
    else:
        # Create Table for JMS Status
        fo.write('<table style="font:normal 12px verdana, arial, helvetica, sans-serif; border:1px solid #1B2E5A" bgcolor="#D7DEEC" width="900" border="0">')
        fo.write('<caption style="font-weight:bold; letter-spacing:10px; border:1px solid #1B2E5A">JMS Runtime Info for :' + serverName + ' </caption>')
        fo.write('<tr align="center" bgcolor="#5F86CF"><td>SERVER</td><td>JMSSERVER</td><td>DestinationName</td><td>DestinationType</td><td>MessagesCurrentCount</td><td>MessagesHighCount</td><td>ConsumersCurrentCount</td><td>ConsumersHighCount</td><td>ConsumersTotalCount</td></tr>')
        for jmsServer in jmsServers:
            jmsServerName = jmsServer.getName();
            destinations = jmsServer.getDestinations();
            rowNum = 0;
            for destination in destinations:
                if destination.getMessagesCurrentCount() >= 0 :
                    # Alternate Report Row Color
                    if rowNum % 2 == 0:
                            rowColor = '#D7DEEC'
                    else:
                            rowColor = '#F4F6FA'

                    fo.write('<tr align="center" bgcolor=' + rowColor + '><td align="left">' + serverName + '  </td><td> ' + jmsServerName + '  </td><td> ' + str(destination.getName()) + ' </td><td> ' + str(destination.getDestinationType()) + '  </td><td> ' + str(destination.getMessagesCurrentCount()) + '  </td><td> ' + str(destination.getMessagesHighCount()) + '   </td><td> ' + str(destination.getConsumersCurrentCount()) + ' </td> <td> ' + str(destination.getConsumersHighCount()) + ' </td> <td> ' + str(destination.getConsumersTotalCount()) + ' </td></tr>')
                    rowNum += 1
        fo.write('</table> <br /><br />')
fo.write('</div>')

#----------------------------------------
# Exit WLST
#----------------------------------------

exit()

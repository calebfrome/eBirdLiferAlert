# -*- coding: utf-8 -*-

import xlrd
import xlwt
import subprocess
import time

get_new_data = False
numAlertSources = 7


class Observation:

    def __init__(self, species, count, date, location, county, state):
        self.species = species
        self.count = count
        self.date = date
        self.location = location
        self.county = county
        self.state = state

    def output(self):
        return [self.species, self.date, self.location, self.county, self.state]


def main():
    if get_new_data:
        # clear raw.txt
        open("raw.txt", 'w').close()

        # run the AHK script to grab the raw data from ebird
        subprocess.Popen("getAlertData.exe getAlertData.ahk", shell=True)
        time.sleep(15 * numAlertSources)

    # open raw.txt
    file = open("raw.txt")

    database = []
    line = ""
    index = 0
    species = ""
    count = ""
    date = ""
    location = ""
    county = ""
    state = ""

    # loop through each alert section
    for x in range(numAlertSources):

        # truncate lines until start of data
        while True:
            line = file.readline()
            if line[:11] == "Needs Alert":
                state = line[16:]
            if line[:7] == "Species":
                break

        # read remainder of file into Observation objects, stored in database
        # read until we see (c) Cornell...
        line = file.readline()
        while line[1] != " ":
            index = line.find("(")
            species = line[:(index - 1 if index >= 0 else -1)]
            file.readline()  # don't keep latin name
            line = file.readline()
            # if there is a confirmed/unconfirmed tag, don't keep it
            if line == "CONFIRMED\n" or line == "UNCONFIRMED\n":
                line = file.readline()
            # determine whether count is X (empty) or a number
            if line[0].isdigit():
                count = line[0]
                date = line[2:(line.find(","))]
            else:
                count = "X"
                date = line[:(line.find(","))]
            file.readline()  # don't keep checklist link
            location = file.readline()[:-1]
            file.readline()  # don't keep map link
            line = file.readline()
            county = line[:(line.find("\t"))]
            line = file.readline()
            # if there is a show details link, don't keep it
            if line == "SHOW DETAILS\n":
                line = file.readline()
            # create Observation object and add to database
            database.append(Observation(species, count, date, location, county, state))

    # compare results with AWM database to determine which would be lifers
    workbook = xlrd.open_workbook('C:/Users/Caleb/Documents/Birds/AMW.xlsx')
    sheet = workbook.sheet_by_name("ABA 7.7.1")
    row = 0
    aba_list = []
    life_list = []
    lifer_needs = []

    while True:
        if str(sheet.cell(row, 0).value) == xlrd.empty_cell.value:
            break
        aba_list.append(sheet.cell(row, 0).value)
        if sheet.cell(row, 1).value == "X":
            life_list.append(sheet.cell(row, 0).value)
        row += 1

    database.sort(key=lambda x: x.species, reverse=False)
    database.sort(key=lambda x: x.state, reverse=True)
    life_list.sort()
    aba_list.sort()

    for o in database:
        if o.species in aba_list and not o.species in life_list:
            lifer_needs.append(o)

    # build html file for output
    output = open("output.html", "w")
    output.write("<html><body><h1>eBird Lifer Alert</h1>")
    if len(lifer_needs) == 0:
        output.write("<p>No lifers reported.</p>")
    else:
        output.write(
            "<table border=1 style=border-collapse:collapse cellpadding=3><tr><th>Species</th><th>Date</th><th>Location</th><th>County</th><th>State</th></tr>")
        for l in lifer_needs:
            output.write("<tr>")
            for x in range(len(l.output())):
                output.write("<td>%s</td>" % l.output()[x])
            output.write("</tr>")
        output.write("</table>")
    output.write("</body></html>")
    output.close()

    # display the results in the browser
    subprocess.Popen("output.html", shell=True)


if __name__ == '__main__':
    main()

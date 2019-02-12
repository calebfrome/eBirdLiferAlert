import subprocess
from bs4 import BeautifulSoup
import mechanize
import http.cookiejar as cj
import json

alert_url_prefix = 'https://ebird.org/ebird/alert/summary?sid='
alert_sids = {'AL': 'SN10344', 'AK': 'SN10345', 'AR': 'SN10346', 'AZ': 'SN10347', 'CA': 'SN10348', 'CO': 'SN10349',
              'CT': 'SN10350', 'DC': 'SN10351', 'DE': 'SN10352', 'FL': 'SN10353', 'GA': 'SN10354', 'HI': 'SN10355',
              'IA': 'SN10356', 'ID': 'SN10357', 'IL': 'SN10358', 'IN': 'SN10359', 'KS': 'SN10360', 'KY': 'SN10361',
              'LA': 'SN10362', 'MA': 'SN10363', 'MD': 'SN10364', 'ME': 'SN10365', 'MI': 'SN10366', 'MN': 'SN10367',
              'MO': 'SN10368', 'MS': 'SN10369', 'MT': 'SN10370', 'NC': 'SN10371', 'ND': 'SN10372', 'NE': 'SN10373',
              'NH': 'SN10374', 'NJ': 'SN10375', 'NM': 'SN10376', 'NV': 'SN10377', 'NY': 'SN10378', 'OH': 'SN10379',
              'OK': 'SN10380', 'OR': 'SN10381', 'PA': 'SN10382', 'RI': 'SN10383', 'SC': 'SN10384', 'SD': 'SN10385',
              'TN': 'SN10386', 'TX': 'SN10387', 'UT': 'SN10388', 'VT': 'SN10389', 'VA': 'SN10390', 'WA': 'SN10391',
              'WI': 'SN10392', 'WV': 'SN10393', 'WY': 'SN10394', 'ABA': 'SN10489'}

life_list_url = 'https://ebird.org/MyEBird?cmd=lifeList&listType=world&listCategory=default&time=life'
aba_list_url = 'https://ebird.org/MyEBird?cmd=lifeList&listType=aba&listCategory=default&time=life'
login_url = 'https://secure.birds.cornell.edu/cassso/login?service=https%3A%2F%2Febird.org%2Flogin%2Fcas%3Fportal%3Debird&locale=en_US'


class Observation:
    def __init__(self, species, count, date, checklist_link, location, map_link, county, state, aba_rare):
        self.species = species
        self.count = count
        self.date = date
        self.checklist_link = checklist_link
        self.location = location
        self.map_link = map_link
        self.county = county
        self.state = state
        self.aba_rare = aba_rare

    def output(self):
        return [self.species, self.date, self.location, '<a href=' + self.map_link + '>Map</a>', self.county,
                self.state, '<a href=' + self.checklist_link + '>Checklist</a>']


def main():
    # Read ABA checklist
    aba_list = {}
    aba_list_file = open('aba_list.txt')
    for line in aba_list_file.readlines():
        species_elements = line.strip().split(',')
        aba_list[species_elements[0]] = int(species_elements[1])

    # Read exceptions
    exceptions_list = []
    exceptions_file = open('exceptions.txt')
    for species in exceptions_file.readlines():
        exceptions_list.append(species.strip())

    # Read config file
    config_data = json.load(open('config.json'))

    # Create web browser
    br = mechanize.Browser()
    bcj = cj.LWPCookieJar()
    br.set_cookiejar(bcj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', 'Chrome')]

    # Open the eBird login page
    br.open(login_url)
    # Select the login form
    br.select_form(nr=0)
    # Set credentials
    br.form['username'] = config_data['credentials']['username']
    br.form['password'] = config_data['credentials']['password']
    # Submit the login form
    br.submit()

    # Scrape life list
    print('scraping life list')
    life_list = []
    life_list_html = BeautifulSoup(br.open(life_list_url).read(), 'html.parser')
    for a in life_list_html.find_all(attrs={'data-species-code': True}):
        life_list.append(str.strip(a.text))

    # Scrape eBird alerts
    print('scraping eBird alerts')
    observation_list = []
    alert_regions = config_data['regions']
    alert_regions.append('ABA' if int(config_data['aba_rare']) in [3, 4, 5] else None)
    for alert_region in alert_regions:
        alert_html = BeautifulSoup(br.open(alert_url_prefix + alert_sids[alert_region]).read(), 'html.parser')
        for tr in alert_html.find_all('tr', class_='has-details'):
            species_name = str.strip(tr.findChild(class_='species-name').findChild('a').text)
            # Filter out species from ABA RBA whose code is below the specified level
            if alert_region == 'ABA':
                if species_name not in aba_list.keys() or aba_list[species_name] < int(config_data['aba_rare']):
                    continue
            species_count = str.strip(tr.findChild(class_='count').text)
            species_date = str.strip(tr.findChild(class_='date').text)[:-10]  # truncate 'Checklist'
            species_checklist_link = 'https://ebird.org' + str.strip(tr.findChild(class_='date').findChild('a')['href'])
            species_location = str.strip(tr.findChild(class_='location').text)[:-4]  # truncate 'Map'
            species_map_link = str.strip(tr.findChild(class_='location').findChild('a')['href'])
            species_county = str.strip(tr.findChild(class_='county').text)
            species_state = str.strip(tr.findChild(class_='state').text).split(',')[0]  # truncate ', United States'
            species_aba_rare = (alert_region == 'ABA')
            observation_list.append(Observation(species_name, species_count, species_date, species_checklist_link,
                                                species_location, species_map_link, species_county, species_state,
                                                species_aba_rare))

    # determine which species would be lifers
    print('creating custom alert')
    observation_list.sort(key=lambda x: x.state, reverse=True)
    observation_list.sort(key=lambda x: x.species, reverse=False)
    lifer_needs = []
    for o in observation_list:
        if o.species not in life_list and o.species not in exceptions_list and (o.species in aba_list.keys() or o.aba_rare):
            lifer_needs.append(o)

    # build output html file
    output = open("output.html", "w")
    output.write("<html><body><h1>eBird Lifer Alert</h1>")
    if len(lifer_needs) == 0:
        output.write("<p>No lifers reported.</p>")
    else:
        output.write(
            '<table border=1 style=border-collapse:collapse cellpadding=3><tr><th>Species</th><th>Date</th>'
            '<th>Location</th><th>Map Link</th><th>County</th><th>State</th><th>Checklist Link</th></tr>')
        for l in lifer_needs:
            output.write("<tr>")
            for td in range(len(l.output())):
                output.write("<td>%s</td>" % l.output()[td])
            output.write("</tr>")
        output.write("</table>")
    output.write("</body></html>")
    output.close()

    # display the results in the browser
    subprocess.Popen("output.html", shell=True)


if __name__ == '__main__':
    main()

import subprocess
from bs4 import BeautifulSoup
import mechanize
import http.cookiejar as cj

alert_url_prefix = 'https://ebird.org/ebird/alert/summary?sid='
alert_sids = {'TX': 'SN10387', 'OK': 'SN10380', 'NM': 'SN10376', 'AZ': 'SN10347', 'CO': 'SN10349', 'KS': 'SN10360',
              'AR': 'SN10346', 'LA': 'SN10362'}

life_list_url = 'https://ebird.org/MyEBird?cmd=lifeList&listType=world&listCategory=default&time=life'
aba_list_url = 'https://ebird.org/MyEBird?cmd=lifeList&listType=aba&listCategory=default&time=life'

login_url = 'https://secure.birds.cornell.edu/cassso/login?service=https%3A%2F%2Febird.org%2Flogin%2Fcas%3Fportal%3Debird&locale=en_US'


class Observation:
    def __init__(self, species, count, date, checklist_link, location, map_link, county, state):
        self.species = species
        self.count = count
        self.date = date
        self.checklist_link = checklist_link
        self.location = location
        self.map_link = map_link
        self.county = county
        self.state = state

    def output(self):
        return [self.species, self.date, self.location, '<a href=' + self.map_link + '>Map</a>', self.county,
                self.state, '<a href=' + self.checklist_link + '>Checklist</a>']


def main():
    # Read ABA checklist
    aba_list = []
    aba_list_file = open('aba_list.txt')
    for species in aba_list_file.readlines():
        aba_list.append(species.strip())

    # Read exceptions
    exceptions_list = []
    exceptions_file = open('exceptions.txt')
    for species in exceptions_file.readlines():
        exceptions_list.append(species.strip())

    # Read credentials
    credentials = {}
    credentials_file = open('credentials.txt')
    credentials['username'] = credentials_file.readline().strip()
    credentials['password'] = credentials_file.readline().strip()

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
    br.form['username'] = credentials['username']
    br.form['password'] = credentials['password']
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
    for alert_sid in alert_sids.values():
        alert_html = BeautifulSoup(br.open(alert_url_prefix + alert_sid).read(), 'html.parser')
        for tr in alert_html.find_all('tr', class_='has-details'):
            species_name = str.strip(tr.findChild(class_='species-name').findChild('a').text)
            species_count = str.strip(tr.findChild(class_='count').text)
            species_date = str.strip(tr.findChild(class_='date').text)[:-10]  # truncate 'Checklist'
            species_checklist_link = 'https://ebird.org' + str.strip(tr.findChild(class_='date').findChild('a')['href'])
            species_location = str.strip(tr.findChild(class_='location').text)
            species_map_link = str.strip(tr.findChild(class_='location').findChild('a')['href'])
            species_county = str.strip(tr.findChild(class_='county').text)
            species_state = str.strip(tr.findChild(class_='state').text).split(',')[0]  # truncate ', United States'
            observation_list.append(Observation(species_name, species_count, species_date, species_checklist_link,
                                                species_location, species_map_link, species_county, species_state))

    # determine which species would be lifers
    print('creating custom alert')
    observation_list.sort(key=lambda x: x.state, reverse=True)
    observation_list.sort(key=lambda x: x.species, reverse=False)
    lifer_needs = []
    for o in observation_list:
        if o.species in aba_list and o.species not in life_list and o.species not in exceptions_list:
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

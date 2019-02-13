import subprocess
from bs4 import BeautifulSoup
import mechanize
import http.cookiejar as cj
import json
import datetime
import calendar
from win10toast import ToastNotifier
import time

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

month_dict = {v: k for k, v in enumerate(calendar.month_abbr)}


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

    def __eq__(self, other):
        return self.species == other.species and self.date == other.date and self.location == other.location

    def output(self):
        return [self.species, self.count, self.date.strftime('%b %d %I:%M %p'), self.location,
                '<a href=' + self.map_link + '>Map</a>', self.state, self.county,
                '<a href=' + self.checklist_link + '>Checklist</a>']


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
    print('scraping eBird alerts:', end=' ')
    observation_list = []
    alert_regions = config_data['regions']
    alert_regions.append('ABA' if int(config_data['aba_rare']) in [3, 4, 5] else None)
    for alert_region in alert_regions:
        print(alert_region, end=' ')
        alert_html = BeautifulSoup(br.open(alert_url_prefix + alert_sids[alert_region]).read(), 'html.parser')
        for tr in alert_html.find_all('tr', class_='has-details'):
            species_name = str.strip(tr.findChild(class_='species-name').findChild('a').text)
            # Filter out species from ABA RBA whose code is below the specified level
            if alert_region == 'ABA':
                if species_name not in aba_list.keys() or aba_list[species_name] < int(config_data['aba_rare']):
                    continue
            species_count = str.strip(tr.findChild(class_='count').text)
            date_str = str.strip(tr.findChild(class_='date').text)[:-10]  # truncate 'Checklist'
            date_month_str = date_str[0:3]
            date_month = month_dict[date_month_str]
            date_day = int(date_str[4:6])
            date_year = int(date_str[8:12])
            date_hour = 0 if len(date_str) < 13 else int(date_str[13:15])    # some reports don't have a time
            date_minute = 0 if len(date_str) < 13 else int(date_str[16:18])  # some reports don't have a time
            species_date = datetime.datetime(date_year, date_month, date_day, date_hour, date_minute)
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
    print('\ncreating custom alert')
    observation_list.sort(key=lambda x: x.state, reverse=True)
    observation_list.sort(key=lambda x: x.species, reverse=False)
    lifer_needs = []
    for o in observation_list:
        if o.species not in life_list and o.species not in exceptions_list and (o.species in aba_list.keys() or o.aba_rare):
            lifer_needs.append(o)

    # Combine reports of the same species based on the config setting
    combined_needs_dict = {}
    if config_data['combine'] in ['county', 'state', 'all']:
        for obs in lifer_needs:
            key_location = 'all'
            if config_data['combine'] == 'county':
                key_location = obs.county
            elif config_data['combine'] == 'state':
                key_location = obs.state
            key = (obs.species, key_location)
            if key not in combined_needs_dict or obs.date > combined_needs_dict[key].date:
                combined_needs_dict[key] = obs

        lifer_needs = combined_needs_dict.values()

    # build output html file
    output = open('alert.html', 'w')
    output.write('<html><body><h1>eBird Lifer Alert</h1>')
    if len(lifer_needs) == 0:
        output.write('<p>No lifers reported.</p>')
    else:
        output.write('<table border=1 style=border-collapse:collapse cellpadding=3><tr><th>Species</th><th>Count</th>'
                     '<th>Date</th><th>Location</th><th>Map Link</th><th>State</th><th>County</th>'
                     '<th>Checklist Link</th></tr>')
        for l in lifer_needs:
            output.write('<tr>')
            for td in range(len(l.output())):
                output.write('<td>%s</td>' % l.output()[td])
            output.write('</tr>')
        output.write('</table>')
    output.write('</body></html>')
    output.close()

    # display the results in the browser
    if config_data['output'] == 'browser':
        subprocess.Popen('alert.html', shell=True)

    # load the previous alert for comparison
    previous_alert = []
    previous_alert_file = open('alert.txt')
    for raw_obs in previous_alert_file.readlines():
        obs = raw_obs.strip().split(',')
        species = obs[0]
        date_str = obs[2]
        date_month = month_dict[date_str[0:3]]
        date_year = datetime.datetime.today().year
        if datetime.datetime.today().month == 1 and date_month == 12:
            date_year -= 1
        date = datetime.datetime(date_year, date_month, int(date_str[4:6]), int(date_str[7:9]), int(date_str[10:12]))
        location = obs[3]
        previous_alert.append(Observation(species, 0, date, '', location, '', '', '', False))

    # display the results as desktop notifications
    if config_data['output'] == 'desktop':
        toaster = ToastNotifier()
        for obs in lifer_needs:
            if obs in previous_alert:
                continue
            toaster.show_toast(obs.species, obs.county + ', ' + obs.state + ' | ' + obs.date,
                               icon_path='ebird_logo.ico', duration=5)
            while toaster.notification_active():
                time.sleep(0.1)

    # write the alert to a file for future reference
    save_data = open('alert.txt', 'w')
    for obs in lifer_needs:
        for item in obs.output():
            save_data.write(str(item) + ',')
        save_data.write('\n')


if __name__ == '__main__':
    main()

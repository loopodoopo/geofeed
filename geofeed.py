#!/usr/bin/python

#Author Maikel de Boer - maikel.deboer@hibernianetworks.com
#Based on: tools.ietf.org/id/draft-google-self-published-geofeeds-02.html

import urllib2, json, netaddr, datetime

mntObject = 'ATRATO-MNT'
output = '/var/www/as5580-opengeofeed.txt'
contact = 'maikel.deboer@hibernianetworks.com'
company = 'Hibernia Networks (AS5580)'

queryurl = 'http://rest.db.ripe.net/search.json?query-string=%s&type-filter=inet6num&type-filter=inetnum&inverse-attribute=mnt-by&flags=no-filtering' % mntObject

def connect_to_ripe(url):
  request = urllib2.urlopen(queryurl)
  data = json.load(request)

  return data

def parse_json(data):
    parse_dict = {} 
    count = 0
    for line in data['objects']['object']:
        key = ''
        value = ''
        #locate the inetnum objects
        if data['objects']['object'][count]['attributes']['attribute'][0]['name'] == 'inet6num':
            key = data['objects']['object'][count]['attributes']['attribute'][0]['value']
        #v4 inetnum objects translate to cidr
        if data['objects']['object'][count]['attributes']['attribute'][0]['name'] == 'inetnum':
            key = translate_inetnum(data['objects']['object'][count]['attributes']['attribute'][0]['value'])
        #Country is not always on the same position. 5 and 6 are added as fail safe, feel free to add 7, 8 etc.
        if data['objects']['object'][count]['attributes']['attribute'][2]['name'] == 'country':
            value = data['objects']['object'][count]['attributes']['attribute'][2]['value']
        if data['objects']['object'][count]['attributes']['attribute'][3]['name'] == 'country':
            value = data['objects']['object'][count]['attributes']['attribute'][3]['value']
        if data['objects']['object'][count]['attributes']['attribute'][4]['name'] == 'country':
            value = data['objects']['object'][count]['attributes']['attribute'][4]['value']
        if data['objects']['object'][count]['attributes']['attribute'][5]['name'] == 'country':
            value = data['objects']['object'][count]['attributes']['attribute'][5]['value']
        if data['objects']['object'][count]['attributes']['attribute'][6]['name'] == 'country':
            value = data['objects']['object'][count]['attributes']['attribute'][6]['value']
        count += 1
        if key:
            parse_dict.update({key:value})
    return parse_dict

def translate_inetnum(inetnum):
    #inetnum objects translate to cidr
    startip = inetnum.split('-')[0]
    endip = inetnum.split('-')[1]
    cidrs = netaddr.iprange_to_cidrs(startip, endip)

    return str(cidrs[0])  

def main():
    ripe_data = connect_to_ripe(queryurl)
    listt = parse_json(ripe_data)
    f = open(output, 'w')
    f.write('#%s Self-published IP Geolocation\n' % company)
    f.write('#This file contains a self-published geofeed as defined in http://tools.ietf.org/html/draft-google-self-published-geofeeds-02\n')
    f.write('#Last update: %s UTC\n' % datetime.datetime.now())
    f.write('#Contact: %s\n' % contact)
    for line in listt:
        f.write('%s,%s,,,\n' % (line, listt[line]))
    f.close()

main()

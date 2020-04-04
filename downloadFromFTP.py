### download files from an ftp server for a range of dates including login
from ftplib import FTP
import datetime
from datetime import timedelta

## log in to ftp server
ftp = FTP('url-of-ftp.de') 
ftp.login("username",'password')
files = ftp.dir('directory/on/ftp/server/')
ftp.cwd('directory/on/ftp/server/')

start_date = datetime.date(2006,11,10)
end_date = datetime.date(2007,1,1)
day_count = (end_date - start_date).days + 1

for date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:
    print(date)
    year = str(date)[0:4]
    mon = str(date)[5:7]
    day = str(date)[8:10]
    folder = year+"_"+mon+"_"+day
    file = 'filename'+str(date)+'file.ending' # creates variable string to fetch a file for each day
    url = 'directory/path'+folder+file 
    file = 'filename'+str(date)+'file.ending'
    ftp.retrbinary(url, open(file, 'wb').write)



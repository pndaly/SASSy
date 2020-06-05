# Crontab Rules
Edit the following `crontab` to reflect your site.

The example below is for a full web-server (via Apache2) and this `crontab` should be enabled under the `root` account.

~~~markdown
# +
# suppress mail
# -
MAILTO=""
# +
# 08:00 am every day, scrape ligo data
# -
0 8 * * * (cd /var/www/SASSy/cron; bash ligo.scrape.sh >> /dev/null 2>&1)
# +
# 08:15 am every day, scrape ligo data (using q3c indexing)
# -
15 8 * * * (cd /var/www/SASSy/cron; bash ligo_q3c.scrape.sh >> /dev/null 2>&1)
# +
# 12:00 pm every day, get latest ZTF file
# -
0 12 * * * (cd /var/www/SASSy/cron; bash ztfgz.pull.sh >> /var/www/SASSy/logs/ztfgz.pull.log 2>&1)
# +
# 12:15 pm every day, unpack latest ZTF file
# -
15 12 * * * (cd /var/www/SASSy/cron; bash ztfgz.unpack.sh >> /var/www/SASSy/logs/ztfgz.unpack.log 2>&1)
# +
# 12:30 pm every day, update database for latest ZTF file
# -
30 12 * * * (cd /var/www/SASSy/cron; nohup bash ztfgz.updatedb.sh >> /var/www/SASSy/logs/ztfgz.updatedb.log 2>&1)
# +
# every hour, scrape tns data (using q3c indexing)
# -
0 * * * * (cd /var/www/SASSy/cron; bash tns_q3c.scrape.sh >> /dev/null 2>&1)
# +
# every half hour, scrape tns data
# -
30 * * * * (cd /var/www/SASSy/cron; bash tns.scrape.sh >> /dev/null 2>&1)
# +
# at 5 minutes past every hour, re-create the SassyCron view in the database
# -
5 * * * * (cd /var/www/SASSy/cron; bash sassy_cron.sh >> /dev/null 2>&1)
~~~

------------------------------------------------------------------------------------------------------------------------

Last Updated: 20191219

#!/bin/bash

REPORT_FILE=../report.xls

cd /root/repos
# clear the report 
cd TH_ANDROID
date > $REPORT_FILE

echo >> $REPORT_FILE
echo TH_ANDROID >> $REPORT_FILE 
../gitinspector/gitinspector/multiple.py --ws=10 --file-types=py,xml,md,java,aidl,properties,gradle >> $REPORT_FILE


cd ../TH_IOS
echo >> $REPORT_FILE
echo TH_IOS >> $REPORT_FILE
../gitinspector/gitinspector/multiple.py --ws=10 --file-types=markdown,mdown,md,c,storyboard,d,mm,h,m,sh,cpp,strings,rb >> $REPORT_FILE

cd ../TH_SVR
echo >> $REPORT_FILE
echo TH_SVR >> $REPORT_FILE
../gitinspector/gitinspector/multiple.py --ws=10 --file-types=less,htm,cshtml,cs,txt,Config,html,config,css,rb,asax,sql,js,scss,md,aspx >> $REPORT_FILE

echo Sending email ...
cd ..
./gitinspector/email_report.py

echo Done.

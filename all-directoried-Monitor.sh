#!/bin/bash

export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:/opt/VRTSob/bin:/etc/vx/bin:/opt/VRTSvcs/bin:/opt/VRTSllt:/opt/VRTS/bin
export SHELL=/bin/bash
export TERM=vt100


WorkingDir=/var/opt/mediation/MMStorage/Working
WorkingDirSDP=/var/opt/mediation/MMStorage/SDP
WorkingDirCCN=/var/opt/mediation/MMStorage/Collection/MBC
WorkingDirAIR=/var/opt/mediation/MMStorage/Collection/AIR
home=`pwd`
IBA=/Backup/Buffers/Auto_Inbuffer_Recovery
OBA=/Backup/Buffers/Auto_Outbuffer_Recovery
mkdir -p $IBA $OBA


PRIORITY=`hostname | awk -F'-' '{print $3}'`
HOST=`hostname | awk -F'-' '{print $1"-"$2}'`
HIGHER=`expr $PRIORITY - 1`

while [ $HIGHER -gt 0 ] ; do
ping -c 3 $HOST"-0"$HIGHER
if [ $? -eq 0 ] ; then exit -3 ; fi
HIGHER=`expr $HIGHER - 1`
done


IFS=$'\n'
ping 10.30.145.89 -c 3 >/dev/null ; if [ $? -eq 0 ] ; then NemoIP=10.30.145.89 ; else NemoIP=10.30.145.89 ; fi
rm -fr *.sms >/dev/null
:> alarm

sendSMS ()
{
for x in `grep -v ^# /Backup/housekeeping/SMS_Contacts |awk -F: '{print $2}'`; do
echo "$x;$*" >> "`echo $SENDER`".sms
done

if [ `ls | grep "sms" | wc -l` -ge 0 ] ; then
echo sftp root@$NemoIP \<\< END                         > ftp_"$$".sh
echo cd "/housekeeping/SMS_sender"                      >>ftp_"$$".sh
echo mput "*.sms"                                       >>ftp_"$$".sh
echo bye                                                >>ftp_"$$".sh
echo END                                                >>ftp_"$$".sh
# Make it execuitable and run it
chmod +x ftp_"$$".sh
./ftp_"$$".sh
rm ./ftp_"$$".sh
rm -fr *.sms >/dev/null
fi
}

if [ `ps -ef | grep MediationMonitor.sh | grep -v grep | wc -l` -gt 3 ] ; then SENDER=ALARM ; sendSMS "Script hanged, please run it manually to check" ; fi

#############################################
##   Checking Server Groups Availability   ##
#############################################

/opt/VRTSvcs/bin/hastatus -sum | egrep "FM|OM" | sed 's/FM_Server_grp/FM_Server1_grp/g' | sed 's/OM_SERVER_grp/OM_SERVER1_grp/g' | grep -v Mediator > .hastatus
/opt/VRTSvcs/bin/hares -display | egrep "FM|OM" | grep grp | grep "^S" | sort -V | awk '{print $1"    "$4}' |  sed 's/FM_Server_grp/FM_Server1_grp/g' |  sed 's/OM_SERVER_grp/OM_SERVER1_grp/g' > .hares

for i in `/opt/VRTSvcs/bin/hastatus -sum | grep FM | awk '{print $2}' | sed 's/FM_Server_grp/FM_Server1_grp/g' | sed 's/FM_SERVER_grp/FM_SERVER1_grp/g' | sort | uniq | sort -V`  ; do

        SERVERGRP_ONLINE=`grep $i .hastatus |  grep    "ONLINE"         | wc -l`
        SERVERGRP_FAULT=`grep $i  .hastatus | egrep "PARTIAL|FAULTED" | wc -l`
        SERVERGRP_FAULT_ID=`grep $i .hastatus | egrep "PARTIAL|FAULTED" | head -1`
        if [ -z $SERVERGRP_FAULT_ID ] ; then SERVERGRP_FAULT_ID="OFFLINE" ; fi

if [ $SERVERGRP_ONLINE -ne 1 ] ; then

        if [ $SERVERGRP_FAULT -gt 0 ]||[ $SERVERGRP_FAULT_ID != "OFFLINE" ]  ; then

        SENDER=`echo $SERVERGRP_FAULT_ID | awk '{print $2}' |sed 's/Server/SvrGrp/g' | sed 's/FM_//g' | sed 's/_grp//g' | sort | uniq`
        FAULT=`echo $SERVERGRP_FAULT_ID | awk '{print $2" "$3" is "$6}' |sed 's/FM_//g' |sed 's/_grp//g' | sed 's/_/-/g' | sed 's/|/ /g'                            | sed 's/Server/ServerGroup/g'`

        sendSMS $FAULT

        elif [ $SERVERGRP_FAULT -eq 0 ]||[ $SERVERGRP_FAULT_ID == "OFFLINE" ]  ; then

        SENDER=`echo $SERVERGRP_FAULT_ID | awk '{print $2}' |sed 's/Server/SvrGrp/g' | sed 's/FM_//g' | sed 's/_grp//g' | sort | uniq`
        FAULT=`echo FM_Server"$i"_grp  $HOST |sed 's/FM_//g' |sed 's/grp //g' | sed 's/_/ /g' | sed 's/-/ /g' |sed 's/|/ /g' |sed 's/Server/ServerGroup_/g'`" is OFFLINE on ALL servers"

        sendSMS $FAULT
        fi

elif [ $SERVERGRP_ONLINE -eq 1 ] ; then

        if [ $SERVERGRP_FAULT -gt 0 ]||[ $SERVERGRP_FAULT_ID != "OFFLINE" ]  ; then

        SENDER=`echo $SERVERGRP_FAULT_ID | awk '{print $2}' |sed 's/Server/SvrGrp/g' | sed 's/FM_//g' | sed 's/_grp//g' | sort | uniq`
        FAULT=`echo $SERVERGRP_FAULT_ID | awk '{print $2" "$3" is "$6}' |sed 's/FM_//g' |sed 's/grp //g' | sed 's/_/ /g' | sed 's/-/ /g'                             | sed 's/|/ /g' | sed 's/Server/ServerGroup/g'`

        sendSMS $FAULT
        fi
fi

if [ $SERVERGRP_ONLINE -gt 1 ] ; then

        SENDER=`echo $SERVERGRP_FAULT_ID | awk '{print $2}' |sed 's/Server/SvrGrp/g' | sed 's/FM_//g' | sed 's/_grp//g' | sort | uniq`
        FAULT=`echo $SERVERGRP_FAULT_ID | awk '{print $2" "$3" is ONLINE on more than ONE server.."}' |sed 's/FM_//g' |sed 's/grp //g' | sed 's/_/ /g'                | sed 's/-/ /g'| sed 's/|/ /g' | sed 's/Server/ServerGroup/g' | head -1`

        sendSMS $FAULT
fi
done

#############################################
##    Listing Mediation Logical Servers    ##
#############################################

ls -ld /var/opt/mediation/MMStorage[0-9]*/Server*/CXC*/storage | awk '{print $9}' |sort -V >.logServs

for i in `cat .logServs | grep -v CXC1737978_R3B` ; do

SERVER=`echo $i | sed 's/\(.*\)\(Server[0-9]*\)\(\/CXC.*\)/\2/'`
SERVERGRP=`grep "$SERVER " .hares | awk '{print $2}'`
SERVICE=`cat $i/config/applications/defaultApplication | awk -F, '{print $2}' | awk -F'.' '{print $1}' | sed 's/%//g' | sed 's/!//g' | sed 's/_/-/g' | sed 's/\&//g' | sed 's/\$//g' | sed 's/\x27//g'`

SERVER_STATUS=`grep $SERVERGRP .hastatus | grep ONLINE | awk '{print $6}'`
SERVER_NODE=`grep $SERVERGRP .hastatus | grep ONLINE | awk '{print $3}' | sed 's/_/-/g'`
if [ -z $SERVER_NODE ] ; then SERVER_NODE=`hostname | awk -F '_' '{print $1}'` ; fi
if [ -z $SERVER_STATUS ] ; then SERVER_STATUS="OFFLINE or PARTIAL" ; fi

##  Input Buffers  ##

        find "$i"/inbuffer -type d  > .inbuffer
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   INPUT buffer accumulation " > .alarmSMS

        for x in `cat .inbuffer` ; do
        CurrentDate=$(date +%s -d "`date "+%Y-%m-%d %H:%M:%S"`")
        Count=`ls -lrth  $x | egrep -v "total|^d" |wc -l`
                cd $x
                OldestFileDate=$(stat -c %y `ls -lrth  $x | egrep -v "^d|^total" | head -1 | awk '{print $9}'`  2>/dev/null | awk -F'.' '{print $1}' )
                cd $home
        if [ -z $OldestFileDate ] ; then OldestDate=$CurrentDate ; else OldestDate=$(date +%s -d "$OldestFileDate") ; fi
        Difference=`echo $(( ($CurrentDate - $OldestDate ) / 60))`

        if [ $Difference -ge 30 ] ; then printf "$x = $Count  " > .alarm ; cat .alarm | tr "\n" " " >> .alarmSMS ; fi
        done

        if [ `cat .alarmSMS | grep inbuffer | wc -l` -gt 0 ] ; then SENDER=IB_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarmSMS`" ; fi
        rm -fr .inbuffer .alarm .alarmSMS

        FILE=`find "$i"/inbuffer -type f -mmin +60 -exec ls -larth {} \;  | sort -k7 | sort -k8 | head -1 | awk '{print $9}'`
        if [ ! -z $FILE ] ; then
        echo $FILE >> $IBA/handled
        mv $FILE $IBA
        fi


##  Output Buffers  ##

        find "$i"/outbuffer -type d  > .outbuffer
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   OUTPUT buffer accumulation " > .alarmSMS

        for x in `cat .outbuffer` ; do
        CurrentDate=$(date +%s -d "`date "+%Y-%m-%d %H:%M:%S"`")
        Count=`ls -lrth  $x | egrep -v "total|^d" |wc -l`
                cd $x
                OldestFileDate=$(stat -c %y `ls -lrth  $x | egrep -v "^d|^total" | head -1 | awk '{print $9}'`  2>/dev/null | awk -F'.' '{print $1}' )
                cd $home
        if [ -z $OldestFileDate ] ; then OldestDate=$CurrentDate ; else OldestDate=$(date +%s -d "$OldestFileDate") ; fi
        Difference=`echo $(( ($CurrentDate - $OldestDate ) / 60))`

        ## Increasing outbuffer time for ODS insertions

        if [ `echo $SERVICE | grep -i ODS | wc -l | sed 's/ //g'` -gt 0 ] ; then timeLimit=60 ; else timeLimit=30 ; fi
        if [ $Difference -ge $timeLimit ] ; then printf "$x = $Count  " > .alarm ; cat .alarm | tr "\n" " " >> .alarmSMS ; fi
        done

        if [ `cat .alarmSMS | grep outbuffer | wc -l` -gt 0 ] ; then SENDER=OB_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarmSMS`" ;fi
        rm -fr .outbuffer .alarm .alarmSMS

        FILE=`find "$i"/outbuffer -type f -mmin +60 -exec ls -larth {} \;  | sort -k7 | sort -k8 | grep -i database | head -1 | awk '{print $9}'`
        if [ ! -z $FILE ] ; then
        echo $FILE >> $OBA/handled
        mv $FILE $OBA
        fi

##  Corrupt  ##

        find $i/corrupt -name "*[0-9]*" -mmin -1440 -exec ls -lrth {} \; | egrep -v "total|^d" > .corrupt

        S=`cat .corrupt | awk '$5 ~ /[0-9]/  {print $0}' | egrep -iv "K|M|G" | wc -l`
        M=`cat .corrupt | awk '$5 ~ /[0-9]K/ {print $0}' | wc -l`
        L=`cat .corrupt | awk '$5 ~ /[0-9]M/ {print $0}' | wc -l`
        O=`cat .corrupt |wc -l`
        A=`ls $i/corrupt | egrep -v "total|^d" | wc -l`
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   CORRUPT files $i/corrupt " > .alarm
        if [ $S -ge 50 ] || [ $M -ge 15 ] || [ $L -ge 3 ] ; then printf " Last 24 hrs = $O  "  >> .alarm ; fi
        if [ $A -ge 300 ] ; then printf " ALL = $A"  >> .alarm ; fi
        if [ `cat .alarm | grep '=' | wc -l` -gt 0 ] ; then SENDER=C_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarm`" ; fi
        rm -fr .corrupt .alarm

##  Duplicate Detection  ##

        find $i/duplicateDetection -name "*[0-9]*" -mmin -1440 -exec ls -lrth {} \; | egrep -v "total|^d" > .duplicateDetection

        S=`cat .duplicateDetection | awk '$5 ~ /[0-9]/  {print $0}' | egrep -iv "K|M|G" | wc -l`
        M=`cat .duplicateDetection | awk '$5 ~ /[0-9]K/ {print $0}' | wc -l`
        L=`cat .duplicateDetection | awk '$5 ~ /[0-9]M/ {print $0}' | wc -l`
        O=`cat .duplicateDetection |wc -l`
        A=`ls $i/duplicateDetection | egrep -v "total|^d" | wc -l`
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   DuplicateDetection files $i/duplicateDetection " > .alarm

        if [ $S -ge 30 ] || [ $M -ge 15 ] || [ $L -ge 2 ] ; then printf " Last 24 hrs = $O  "  >> .alarm ; fi
        if [ $A -ge 300 ] ; then printf "ALL = $A"  >> .alarm ; fi
        if [ `cat .alarm | grep '=' | wc -l` -gt 0 ] ; then SENDER=DD_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarm`" ; fi
        rm -fr .duplicateDetection .alarm

##  Duplicate File  ##

        find $i/duplicateFile -name "*[0-9]*" -mmin -1440 -exec ls -lrth {} \; | egrep -v "total|^d" > .duplicateFile

        S=`cat .duplicateFile | awk '$5 ~ /[0-9]/  {print $0}' | egrep -iv "K|M|G" | wc -l`
        M=`cat .duplicateFile | awk '$5 ~ /[0-9]K/ {print $0}' | wc -l`
        L=`cat .duplicateFile | awk '$5 ~ /[0-9]M/ {print $0}' | wc -l`
        O=`cat .duplicateFile |wc -l`
        A=`ls $i/duplicateFile | egrep -v "total|^d" | wc -l`
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   DuplicateFile files $i/duplicateFile " > .alarm

        if [ $S -ge 30 ] || [ $M -ge 15 ] || [ $L -ge 2 ] ; then printf " Last 24 hrs = $O  "  >> .alarm ; fi
        if [ $A -ge 300 ] ; then printf "ALL = $A"  >> .alarm ; fi
        if [ `cat .alarm | grep '=' | wc -l` -gt 0 ] ; then SENDER=DF_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarm`" ; fi
        rm -fr .duplicateFile .alarm

##  Incomplete  ##

        find $i/incomplete -name "*[0-9]*" -mmin -1440 -exec ls -lrth {} \; | egrep -v "total|^d" > .incomplete

        S=`cat .incomplete | awk '$5 ~ /[0-9]/  {print $0}' | egrep -iv "K|M|G" | wc -l`
        M=`cat .incomplete | awk '$5 ~ /[0-9]K/ {print $0}' | wc -l`
        L=`cat .incomplete | awk '$5 ~ /[0-9]M/ {print $0}' | wc -l`
        O=`cat .incomplete |wc -l`
        A=`ls $i/incomplete | egrep -v "total|^d" | wc -l`
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   Incomplete files $i/incomplete " > .alarm

        if [ $S -ge 30 ] || [ $M -ge 15 ] || [ $L -ge 2 ] ; then printf " Last 24 hrs = $O  "  >> .alarm ; fi
        if [ $A -ge 300 ] ; then printf "ALL = $A"  >> .alarm ; fi
        if [ `cat .alarm | grep '=' | wc -l` -gt 0 ] ; then SENDER=IC_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarm`" ; fi
        rm -fr .incomplete .alarm

##  Unconfirmed  ##

        find $i/unconfirmed -name "*[0-9]*"  -type f -size 0  -exec rm -f {} \;

        find $i/unconfirmed -name "*[0-9]*" -mmin -1440 -exec ls -lrth {} \;  | egrep -v "total|^d" > .unconfirmed

        S=`cat .unconfirmed | awk '$5 ~ /[0-9]/  {print $0}' | egrep -iv "K|M|G" | wc -l`
        M=`cat .unconfirmed | awk '$5 ~ /[0-9]K/ {print $0}' | wc -l`
        L=`cat .unconfirmed | awk '$5 ~ /[0-9]M/ {print $0}' | wc -l`
        O=`cat .unconfirmed |wc -l`
        A=`ls $i/unconfirmed | egrep -v "total|^d" | wc -l`
        printf "$SERVER $SERVER_NODE $SERVER_STATUS $SERVICE   Unconfirmed files $i/unconfirmed " > .alarm

        if [ $S -ge 30 ] || [ $M -ge 15 ] || [ $L -ge 2 ] ; then printf " Last 24 hrs = $O  "  >> .alarm ; fi
        if [ $A -ge 300 ] ; then printf "ALL = $A"  >> .alarm ; fi
        if [ `cat .alarm | grep '=' | wc -l` -gt 0 ] ; then SENDER=UC_`echo $SERVER | sed 's/Server/Svr/g'` ; sendSMS "`cat .alarm`" ; fi
        rm -fr .unconfirmed .alarm
done
#############################################
##  Listing Mediation Working Directories  ##
#############################################

ID=0
find $WorkingDir -type d | grep -v 'MBC6.*input.*fileslices.....Server' > .working_dir_all
        #ID=0
        for x in `cat .working_dir_all | grep -v TestingUsage` ; do
        Count=`ls $x | grep -v "^Seq" | grep -v "^Transaction" |wc -l`
        if [ $Count -ge 500 ] ; then printf "Accumulation in $x = $Count  " > .alarm ; cat .alarm | tr "\n" " " > .alarmSMS
        SENDER=`hostname | awk -F'-' '{print $1"_"$2}' | sed 's/_PHY//g'`$ID ; sendSMS "`cat .alarmSMS`"
        ID=`expr $ID + 1`
        fi
        done

       # rm -fr .working_dir_all .alarm .alarmSMS

find $WorkingDirSDP -type d  > .working_dir_sdp
        #ID=0
        for x in `cat .working_dir_sdp | grep -v TestingUsage` ; do
        Count=`ls $x | grep -v "^Seq" | grep -v "^Transaction" |wc -l`
        if [ $Count -ge 300 ] ; then printf "Accumulation in $x = $Count  " > .alarm ; cat .alarm | tr "\n" " " > .alarmSMS
        SENDER=`hostname | awk -F'-' '{print $1"_"$2}' | sed 's/_PHY//g'`$ID ; sendSMS "`cat .alarmSMS`"
        ID=`expr $ID + 1`
        fi
        done

find $WorkingDirCCN -type d  > .working_dir_ccn
        #ID=0
        for x in `cat .working_dir_ccn | grep -v TestingUsage` ; do
        Count=`ls $x | grep -v "^Seq" | grep -v "^Transaction" |wc -l`
        if [ $Count -ge 300 ] ; then printf "Accumulation in $x = $Count  " > .alarm ; cat .alarm | tr "\n" " " > .alarmSMS
        SENDER=`hostname | awk -F'-' '{print $1"_"$2}' | sed 's/_PHY//g'`$ID ; sendSMS "`cat .alarmSMS`"
        ID=`expr $ID + 1`
        fi
        done

       # rm -fr .working_dir_ccn .alarm .alarmSMS

find $WorkingDirAIR -type d  > .working_dir_air
        #ID=0
        for x in `cat .working_dir_air | grep -v TestingUsage | grep -v Trigging_Scripts | grep -v "*.sh"` ; do
        Count=`ls $x | grep -v "^Seq" | grep -v "^Transaction" |wc -l`
        if [ $Count -ge 300 ] ; then printf "Accumulation in $x = $Count  " > .alarm ; cat .alarm | tr "\n" " " > .alarmSMS
        SENDER=`hostname | awk -F'-' '{print $1"_"$2}' | sed 's/_PHY//g'`$ID ; sendSMS "`cat .alarmSMS`"
        ID=`expr $ID + 1`
        fi
        done
rm .hastatus .hares .logServs

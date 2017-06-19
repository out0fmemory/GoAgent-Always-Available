#!/bin/bash

# name
gen_all() {
    cnt=`git --git-dir=.git --work-tree=.  rev-list HEAD --count`
    all_name='history_all_ips/'${1}_all.txt
    rm -f ${all_name}
    echo -n "|" > seperator
    for (( i = 0; i < cnt; i++ )); do
        git show HEAD~$i:${1} > tem
        temStr=`cat tem`
        temStr=${temStr//\r\n/""}
        temStr=${temStr//\r/""}
        temStr=${temStr//\n/""}
        echo -n ${temStr} > tem
#        temStr=`cat tem | grep \|`
#        if [ -z $temStr ]; then
#            echo 'empty ips start'
#            cat tem
#            echo 'empty ips end'
#            rm -f tem
        if [ -z ${temStr} ]; then
            echo 'empty ips'
        elif [[ ${temStr} == '*fatal*' ]]; then
            echo 'not legal ,end'
            rm -f seperator
            rm -f tem
            break
        else
            echo "get ips start${i}"
            echo ${temStr}
            echo "get ips end${i}"
            cat tem >> ${all_name}
            cat seperator >> ${all_name}
            rm -f tem
        fi
    done
    rm -f seperator
    rm -f tem
}

gen_all 铁通宽带高稳定性Ip.txt
gen_all 电信宽带高稳定性Ip.txt
gen_all 阿里云多线高稳定性Ip.txt
#gen_all googleip.txt
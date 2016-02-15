#! /bin/sh
#
# goagentvps init script
#

### BEGIN INIT INFO
# Provides:          goagentvps
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Should-Start:      $local_fs
# Should-Stop:       $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Monitor for goagentvps activity
# Description:       goagentvps is python wsgi server.
### END INIT INFO

# **NOTE** bash will exit immediately if any command exits with non-zero.
set -e

PACKAGE_NAME=goagentvps
PACKAGE_DESC="python goagentvps"
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

start() {
    echo -n "Starting ${PACKAGE_DESC}: "
    PYTHONPATH=$(/usr/bin/env python -c "print ':'.join(__import__('glob').glob('*.egg')),"):${PYTHONPATH} \
        /usr/bin/env python -m supervisor.supervisord -c ./supervisord-${PACKAGE_NAME}.conf
    echo "${PACKAGE_NAME}."
    echo "sudo tail -F /opt/${PACKAGE_NAME}/log/*.log to view logs"
}

stop() {
    echo -n "Stopping ${PACKAGE_DESC}: "
    kill `ps aux | grep -v grep | grep supervisord-${PACKAGE_NAME} | awk '{print $2}'` 2>/dev/null || true
    echo "${PACKAGE_NAME}."
}

restart() {
    stop
    sleep 1
    start
}

usage() {
    N=$(basename "$0")
    echo "Usage: sudo $N {start|stop|restart}" >&2
    exit 1
}

if [ "$(id -u)" != "0" ]; then
    echo "please use sudo to run ${PACKAGE_NAME}"
    exit 0
fi

cd $(dirname $(readlink -f "$0"))

if [ -f /usr/local/${PACKAGE_NAME}/${PACKAGE_NAME}.sh ]; then
    cd /usr/local/${PACKAGE_NAME}
fi

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  #reload)
  restart|force-reload)
    restart
    ;;
  *)
    usage
    ;;
esac

exit 0

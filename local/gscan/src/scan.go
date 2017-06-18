package main

import (
	"crypto/tls"
	"log"
	"math/rand"
	"net"
	"net/http"
	"net/http/httputil"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

type ScanRecord struct {
	IP         string
	MatchHosts []string
	PingRTT    time.Duration
	SSLRTT     time.Duration

	httpVerifyTimeout time.Duration
}
type ScanRecordArray []*ScanRecord
type ScanOptions struct {
	Config *GScanConfig

	recordMutex sync.Mutex
	hostsMutex  sync.Mutex
	inputHosts  HostIPTable
	records     ScanRecordArray

	scanCounter int32
}

func (options *ScanOptions) AddRecord(rec *ScanRecord) {
	options.recordMutex.Lock()
	if nil == options.records {
		options.records = make(ScanRecordArray, 0)
	}
	options.records = append(options.records, rec)
	options.recordMutex.Unlock()
	log.Printf("Found a record: IP=%s, SSLRTT=%fs\n", rec.IP, rec.SSLRTT.Seconds())
}

func (options *ScanOptions) IncScanCounter() {
	atomic.AddInt32(&(options.scanCounter), 1)
	if options.scanCounter%1000 == 0 {
		log.Printf("Scanned %d IPs\n", options.scanCounter)
	}
}

func (options *ScanOptions) RecordSize() int {
	options.recordMutex.Lock()
	defer options.recordMutex.Unlock()
	return len(options.records)
}

func (options *ScanOptions) SSLMatchHosts(conn *tls.Conn) []string {
	hosts := make([]string, 0)
	options.hostsMutex.Lock()
	for _, host := range options.inputHosts {
		testhost := host.Host
		if strings.Contains(testhost, ".appspot.com") {
			testhost = "appengine.google.com"
		} else if strings.Contains(testhost, "ggpht.com") {
			testhost = "googleusercontent.com"
		} else if strings.Contains(testhost, ".books.google.com") {
			testhost = "books.google.com"
		} else if strings.Contains(testhost, ".googleusercontent.com") {
			testhost = "googleusercontent.com"
		}
		if conn.VerifyHostname(testhost) == nil {
			hosts = append(hosts, host.Host)
		}
	}
	options.hostsMutex.Unlock()
	dest := make([]string, len(hosts))
	perm := rand.Perm(len(hosts))
	for i, v := range perm {
		dest[v] = hosts[i]
	}
	hosts = dest
	return hosts
}

func (options *ScanOptions) HaveHostInRecords(host string) bool {
	options.hostsMutex.Lock()
	defer options.hostsMutex.Unlock()
	_, exists := options.inputHosts[host]
	return !exists
}

func (options *ScanOptions) RemoveFromInputHosts(hosts []string) {
	options.hostsMutex.Lock()
	for _, host := range hosts {
		delete(options.inputHosts, host)
	}
	options.hostsMutex.Unlock()
}

func (records *ScanRecordArray) Len() int {
	return len(*records)
}

func (records *ScanRecordArray) Less(i, j int) bool {
	return (*records)[i].SSLRTT < (*records)[j].SSLRTT
}

func (records *ScanRecordArray) Swap(i, j int) {
	tmp := (*records)[i]
	(*records)[i] = (*records)[j]
	(*records)[j] = tmp
}

func matchHostnames(pattern, host string) bool {
	if len(pattern) == 0 || len(host) == 0 {
		return false
	}
	patternParts := strings.Split(pattern, ".")
	hostParts := strings.Split(host, ".")

	if len(patternParts) != len(hostParts) {
		return false
	}

	for i, patternPart := range patternParts {
		if patternPart == "*" {
			continue
		}
		if patternPart != hostParts[i] {
			return false
		}
	}
	return true
}

func find_match_hosts(conn *tls.Conn, options *ScanOptions, record *ScanRecord) bool {
	if nil == record.MatchHosts || len(record.MatchHosts) == 0 {
		record.MatchHosts = options.SSLMatchHosts(conn)
	}

	newhosts := make([]string, 0)
	for _, host := range record.MatchHosts {
		if options.HaveHostInRecords(host) {
			continue
		}
		newhosts = append(newhosts, host)
		valid := true
		for _, pattern := range options.Config.ScanGoogleHosts.HTTPVerifyHosts {
			if matchHostnames(pattern, host) {
				conn.SetReadDeadline(time.Now().Add(record.httpVerifyTimeout))
				req, _ := http.NewRequest("HEAD", "https://"+host, nil)
				res, err := httputil.NewClientConn(conn, nil).Do(req)
				if nil != err || res.StatusCode >= 400 {
					valid = false
				}
				break
			}
		}
		if valid {
			newhosts = append(newhosts, host)
		}
	}
	record.MatchHosts = newhosts
	return len(record.MatchHosts) > 0
}

func test_conn(conn *tls.Conn, options *ScanOptions, record *ScanRecord) bool {
	//check SSL certificate
	success := false
	for _, cert := range conn.ConnectionState().PeerCertificates {
		for _, verifyHost := range options.Config.ScanGoogleIP.SSLCertVerifyHosts {
			if cert.VerifyHostname(verifyHost) != nil {
				return false
			} else {
				success = true
			}
		}
		if success {
			break
		}
	}
	for _, verifyHost := range options.Config.ScanGoogleIP.HTTPVerifyHosts {
		conn.SetReadDeadline(time.Now().Add(record.httpVerifyTimeout))
		req, _ := http.NewRequest("HEAD", "https://"+verifyHost, nil)
		res, err := httputil.NewClientConn(conn, nil).Do(req)
		if nil != err || res.StatusCode >= 400 {
			return false
		}
	}
	return true
}

func testip_once(ip string, options *ScanOptions, record *ScanRecord) bool {
	start := time.Now()
	var end time.Time
	pingRTT := (options.Config.ScanMinPingRTT + options.Config.ScanMaxPingRTT) / 2
	if options.Config.VerifyPing {
		err := Ping(ip, options.Config.ScanMaxPingRTT)
		if err != nil {
			log.Printf("####error ip:%s for %v", ip, err)
			return false
		}
		end = time.Now()
		if nil == err {
			if options.Config.ScanMinPingRTT > 0 && end.Sub(start) < options.Config.ScanMinPingRTT {
				return false
			}
			pingRTT = end.Sub(start)
		}
	}
	record.PingRTT = record.PingRTT + pingRTT
	addr := net.JoinHostPort(ip, "443")
	var config tls.Config
	config.InsecureSkipVerify = true

	dialer := new(net.Dialer)
	dialer.Timeout = options.Config.ScanMaxSSLRTT
	conn, err := tls.DialWithDialer(dialer, "tcp", addr, &config)
	if err != nil {
		//log.Printf("####ssl dial:%v", err)
		return false
	}
	end = time.Now()
	sslRTT := end.Sub(start)
	if options.Config.ScanMinSSLRTT > 0 && sslRTT < options.Config.ScanMinSSLRTT {
		conn.Close()
		return false
	}

	success := true
	record.httpVerifyTimeout = options.Config.ScanMaxSSLRTT - sslRTT
	if options.Config.scanIP {
		success = test_conn(conn, options, record)
	} else {
		success = find_match_hosts(conn, options, record)
	}
	//end = time.Now()
	conn.Close()
	if success {
		record.SSLRTT = record.SSLRTT + sslRTT
	}
	return success
}

func testip(ip string, options *ScanOptions) *ScanRecord {
	record := new(ScanRecord)
	record.IP = ip
	for i := 0; i < options.Config.ScanCountPerIP; i++ {
		if !testip_once(ip, options, record) {
			return nil
		}
	}
	record.PingRTT = record.PingRTT / time.Duration(options.Config.ScanCountPerIP)
	record.SSLRTT = record.SSLRTT / time.Duration(options.Config.ScanCountPerIP)
	return record
}

func testip_worker(ch chan string, options *ScanOptions, w *sync.WaitGroup) {
	for ip := range ch {
		if len(ip) == 0 {
			w.Done()
			break
		}
		record := testip(ip, options)
		if nil != record {
			if !options.Config.scanIP {
				options.RemoveFromInputHosts(record.MatchHosts)
			}
			options.AddRecord(record)
		}
		options.IncScanCounter()
	}
}

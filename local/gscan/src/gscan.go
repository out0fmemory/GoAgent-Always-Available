package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

type ScanGoogleIPConfig struct {
	HTTPVerifyHosts    []string
	SSLCertVerifyHosts []string
	RecordLimit        int
	OutputFile         string
	OutputSeparator    string
}

type ScanGoogleHostsConfig struct {
	InputHosts      string
	OutputHosts     string
	HTTPVerifyHosts []string
}

type GScanConfig struct {
	VerifyPing     bool
	ScanMinPingRTT time.Duration
	ScanMaxPingRTT time.Duration
	ScanMinSSLRTT  time.Duration
	ScanMaxSSLRTT  time.Duration
	ScanWorker     int
	ScanCountPerIP int

	Operation       string
	scanIP          bool
	ScanGoogleIP    ScanGoogleIPConfig
	ScanGoogleHosts ScanGoogleHostsConfig
}

func main() {
	iprange_file := flag.String("iprange", "./iprange.conf", "IP Range file")
	conf_file := flag.String("conf", "./gscan.conf", "Config file, json format")
	flag.Parse()
	conf_content, err := ioutil.ReadFile(*conf_file)
	if nil != err {
		fmt.Printf("%v\n", err)
		return
	}
	var cfg GScanConfig
	err = json.Unmarshal(conf_content, &cfg)
	if nil != err {
		fmt.Printf("%v\n", err)
		return
	}
	cfg.scanIP = strings.EqualFold(cfg.Operation, "ScanGoogleIP")
	cfg.ScanMaxSSLRTT = cfg.ScanMaxSSLRTT * time.Millisecond
	cfg.ScanMinSSLRTT = cfg.ScanMinSSLRTT * time.Millisecond
	cfg.ScanMaxPingRTT = cfg.ScanMaxPingRTT * time.Millisecond
	cfg.ScanMinPingRTT = cfg.ScanMinPingRTT * time.Millisecond

	var outputfile *os.File
	var outputfile_path string
	if cfg.scanIP {
		outputfile_path = cfg.ScanGoogleIP.OutputFile
	} else {
		outputfile_path = cfg.ScanGoogleHosts.OutputHosts
	}
	outputfile_path, _ = filepath.Abs(outputfile_path)
	outputfile, err = os.OpenFile(outputfile_path, os.O_CREATE|os.O_TRUNC|os.O_RDWR, 0644)
	if nil != err {
		fmt.Printf("%v\n", err)
		return
	}
	options := ScanOptions{
		Config: &cfg,
	}
	if !cfg.scanIP {
		options.inputHosts, err = parseHostsFile(cfg.ScanGoogleHosts.InputHosts)
		if nil != err {
			fmt.Printf("%v\n", err)
			return
		}
	}
	log.Printf("Start loading IP Range file:%s\n", *iprange_file)
	ipranges, err := parseIPRangeFile(*iprange_file)
	if nil != err {
		fmt.Printf("%v\n", err)
		return
	}
	worker_count := cfg.ScanWorker
	ch := make(chan string)
	var w sync.WaitGroup
	w.Add(worker_count)
	for i := 0; i < worker_count; i++ {
		go testip_worker(ch, &options, &w)
	}

	log.Printf("Start scanning available IP\n")
	start_time := time.Now()
	eval_count := 0
	for _, iprange := range ipranges {
		var i int64
		for i = iprange.StartIP; i <= iprange.EndIP; i++ {
			ch <- inet_ntoa(i).String()
			eval_count = eval_count + 1

			if cfg.scanIP {
				if options.RecordSize() >= cfg.ScanGoogleIP.RecordLimit {
					goto _end
				}
			} else {
				if len(options.inputHosts) == 0 {
					goto _end
				}
			}
		}
	}

_end:
	for i := 0; i < worker_count; i++ {
		ch <- ""
	}
	w.Wait()
	close(ch)
	log.Printf("Scanned %d IP in %fs, found %d records\n", eval_count, time.Now().Sub(start_time).Seconds(), len(options.records))
	sort.Sort(&(options.records))
	if cfg.scanIP {
		ss := make([]string, 0)
		for _, rec := range options.records {
			ss = append(ss, rec.IP)
		}
		_, err = outputfile.WriteString(strings.Join(ss, cfg.ScanGoogleIP.OutputSeparator))
		if nil != err {
			log.Printf("Failed to write output file:%s for reason:%v\n", outputfile_path, err)
		}
	} else {
		outputfile.WriteString(fmt.Sprintf("###############Update %s###############\n", time.Now().Format("2006-01-02 15:04:05")))
		outputfile.WriteString("###############GScan Hosts Begin#################\n")
		domains_set := make(map[string]int)
		for _, rec := range options.records {
			for _, domain := range rec.MatchHosts {
				if _, exists := domains_set[domain]; !exists {
					outputfile.WriteString(fmt.Sprintf("%s\t%s\n", rec.IP, domain))
					domains_set[domain] = 1
				}
			}
		}
		outputfile.WriteString("###############GScan Hosts End##################\n")
		outputfile.WriteString("\n")
		outputfile.WriteString("#No available IP found,inherit from input\n")
		for _, h := range options.inputHosts {
			outputfile.WriteString(fmt.Sprintf("%s\t%s\n", h.IP, h.Host))
		}
	}

	err = outputfile.Close()
	if nil != err {
		log.Printf("Failed to close output file:%s for reason:%v\n", outputfile_path, err)
	} else {
		log.Printf("All results writed to %s\n", outputfile_path)
	}

}

package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

type HostIP struct {
	Host      string
	IP        string
//	Verifying bool
}

type HostIPTable map[string]HostIP

func parseHostsFile(file string) (HostIPTable, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	hosts := make(HostIPTable)
	scanner := bufio.NewScanner(f)
	lineno := 1
	for scanner.Scan() {
		line := scanner.Text()
		line = strings.TrimSpace(line)
		//comment start with '#'
		if strings.HasPrefix(line, "#") || len(line) == 0 {
			continue
		}
		ss := strings.Fields(line)
		if len(ss) != 2 {
			return nil, fmt.Errorf("Invalid line:%d in hosts file:%s", lineno, file)
		}
		
		pair := HostIP{
			Host:      ss[1],
			IP:        ss[0],
//			Verifying: false,
		}
		hosts[ss[1]] = pair
		lineno = lineno + 1
	}
	return hosts, nil
}

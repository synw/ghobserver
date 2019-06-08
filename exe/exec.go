package exe

import (
	"fmt"
	"os/exec"
	"strings"

	"github.com/synw/terr"
)

func Exec(cmdName string, cmdArgs ...string) (string, *terr.Trace) {
	// Execute a python script
	cmd := exec.Command("python3", cmdArgs...)
	out, err := cmd.CombinedOutput()
	msg := fmt.Sprintf("%s\n", out)
	msg = strings.Replace(string(out), "\n", "", -1)
	if err != nil {
		errmsg := "Error executing command " + cmdName + ":\n" + msg + "\nERR:" + err.Error()
		tr := terr.New(errmsg)
		return "", tr
	}
	return msg, nil
}

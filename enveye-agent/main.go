package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"time"
	"bytes"
	"mime/multipart"
	"io"
	"os/exec"
	"strings"
)

// Snapshot represents the structure of the snapshot to be generated
type Snapshot struct {
	ApplicationName     string                 `json:"application_name"`
	ApplicationType     string                 `json:"application_type"`
	EnvironmentContext  map[string]interface{} `json:"environment_context"`
	Timestamp           string                 `json:"timestamp"`
}

// getOSInfo returns a map with the current OS details
func getOSInfo() map[string]string {
	return map[string]string{
		"name":         runtime.GOOS,
		"architecture": runtime.GOARCH,
	}
}

// readEnvVariables reads the values of the given environment variables
func readEnvVariables(keys []string) map[string]string {
	env := make(map[string]string)
	for _, key := range keys {
		val, found := os.LookupEnv(key)
		if !found {
			val = "Not Set"
		}
		env[key] = val
	}
	return env
}

// writeJSONToFile writes the snapshot data to a JSON file
func writeJSONToFile(data Snapshot, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	return encoder.Encode(data)
}

// computeSHA256 computes the SHA256 hash for a file
func computeSHA256(path string) string {
	file, err := os.Open(path)
	if err != nil {
		return "error: " + err.Error()
	}
	defer file.Close()

	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "error: " + err.Error()
	}
	return hex.EncodeToString(hash.Sum(nil))
}

// uploadSnapshot uploads the snapshot to the given URL
func uploadSnapshot(uploadURL string, filePath string, hostname string, appPath string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("snapshot", filepath.Base(filePath))
	if err != nil {
		return err
	}
	_, err = io.Copy(part, file)

	writer.WriteField("hostname", hostname)
	writer.WriteField("app_path", appPath)

	err = writer.Close()
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", uploadURL, body)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("upload failed: %s\n%s", resp.Status, string(respBody))
	}

	fmt.Println("✅ Upload successful!")
	return nil
}

// scanAppFolder walks through the application folder and returns the relevant file details
func scanAppFolder(folder string) map[string]map[string]interface{} {
	results := make(map[string]map[string]interface{})

	err := filepath.Walk(folder, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		ext := filepath.Ext(path)
		validExts := map[string]bool{
			".dll":    true,
			".so":     true,
			".dylib":  true,
			".config": true,
			".json":   true,
			".xml":    true,
		}

		if validExts[ext] {
			relPath, _ := filepath.Rel(folder, path)
			results[relPath] = map[string]interface{}{
				"size_bytes": info.Size(),
				"modified":   info.ModTime().Format(time.RFC3339),
				"sha256":     computeSHA256(path),
			}
		}
		return nil
	})

	if err != nil {
		results["error"] = map[string]interface{}{
			"message": err.Error(),
		}
	}

	return results
}

// checkServiceStatus checks the status of a service on the system
func checkServiceStatus(service string) string {
	switch runtime.GOOS {
	case "linux":
		return runCmd("systemctl", "is-active", service)
	case "darwin":
		return runCmd("launchctl", "list", service)
	case "windows":
		return runCmd("powershell", "Get-Service", "-Name", service, "|", "Select-Object", "-ExpandProperty", "Status")
	default:
		return "unsupported platform"
	}
}

// runCmd runs a system command and returns the output
func runCmd(name string, args ...string) string {
	out, err := exec.Command(name, args...).CombinedOutput()
	if err != nil {
		return "error: " + err.Error()
	}
	return strings.TrimSpace(string(out))
}

// defaultServicesByPlatform returns the default services to check based on the platform
func defaultServicesByPlatform() []string {
	switch runtime.GOOS {
	case "windows":
		return []string{"W3SVC", "MSSQL$SQLEXPRESS", "MongoDB", "RabbitMQ", "AppHostSvc", "WinRM"}
	case "linux":
		return []string{"nginx", "apache2", "mysql", "mariadb", "postgresql", "mongodb", "redis", "docker", "sshd", "systemd-journald"}
	case "darwin":
		return []string{"homebrew.mxcl.nginx", "homebrew.mxcl.postgresql", "homebrew.mxcl.mongodb-community", "com.apple.sshd"}
	default:
		return []string{}
	}
}

// main function to handle the process of collecting system information and uploading it
func main() {
	appFolder := flag.String("app-folder", "", "Path to the application folder")
	appType := flag.String("app-type", "", "Application type: desktop or web")
	uploadURL := flag.String("upload-url", "", "Optional: Upload URL")
	extraServicesFlag := flag.String("extra-services", "", "Comma-separated list of extra service names to check")
	outputFile := flag.String("output", "", "Optional: Custom output filename for the snapshot")
	snapshotLabel := flag.String("label", "", "Optional: Label snapshot as good or faulty")

	flag.Parse()

	if *appFolder == "" || *appType == "" {
		fmt.Println("❌ Error: --app-folder and --app-type are required")
		os.Exit(1)
	}

	// Gather the list of required services
	requiredServices := defaultServicesByPlatform()
	if *extraServicesFlag != "" {
		extras := strings.Split(*extraServicesFlag, ",")
		for _, svc := range extras {
			svc = strings.TrimSpace(svc)
			if svc != "" {
				requiredServices = append(requiredServices, svc)
			}
		}
	}

	// Check the status of each service
	serviceStatuses := make(map[string]string)
	for _, svc := range requiredServices {
		serviceStatuses[svc] = checkServiceStatus(svc)
	}

	// Generate the snapshot filename
	execPath, err := os.Executable()
	if err != nil {
		fmt.Printf("❌ Failed to get executable path: %v\n", err)
		os.Exit(1)
	}
	baseDir := filepath.Dir(execPath)

	osTag := map[string]string{
		"windows": "WIN",
		"linux":   "LIN",
		"darwin":  "MAC",
	}[runtime.GOOS]
	if osTag == "" {
		osTag = "GEN"
	}

	labelSuffix := ""
	if *snapshotLabel != "" {
		labelSuffix = "_" + strings.ToUpper(*snapshotLabel)
	}

	hostname := hostname()
	appName := filepath.Base(*appFolder)
	timestamp := time.Now().Format("20060102T150405")
	fileName := fmt.Sprintf("%s_%s_%s_%s%s.json", hostname, appName, osTag, timestamp, labelSuffix)

	// Determine where to save the snapshot file
	snapshotPath := ""
	if *outputFile != "" {
		if filepath.IsAbs(*outputFile) {
			snapshotPath = *outputFile
		} else {
			snapshotPath = filepath.Join(baseDir, *outputFile)
		}
	} else {
		snapshotPath = filepath.Join(baseDir, fileName)
	}

	// Create the snapshot data
	snapshot := Snapshot{
		ApplicationName: filepath.Base(*appFolder),
		ApplicationType: *appType,
		EnvironmentContext: map[string]interface{}{
			"os_info":                        getOSInfo(),
			"critical_environment_variables": readEnvVariables([]string{"APP_ENV", "ENVIRONMENT"}),
			"app_folder_files":               scanAppFolder(*appFolder),
			"required_services_status":       serviceStatuses,
		},
		Timestamp: time.Now().Format(time.RFC3339),
	}

	// Write the snapshot data to the file
	if err := writeJSONToFile(snapshot, snapshotPath); err != nil {
		fmt.Printf("❌ Failed to write snapshot: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("✅ Snapshot written to %s\n", snapshotPath)

	// Upload the snapshot if an upload URL is provided
	if *uploadURL != "" {
		err := uploadSnapshot(*uploadURL, snapshotPath, hostname, *appFolder)
		if err != nil {
			fmt.Printf("❌ Upload failed: %v\n", err)
		}
	}
}

// hostname returns the hostname of the system
func hostname() string {
	name, err := os.Hostname()
	if err != nil {
		return "unknown"
	}
	return name
}

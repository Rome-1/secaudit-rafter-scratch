package main

import (
"crypto/tls"
"fmt"
"net/http"

"github.com/go-git/go-git/v5"
"github.com/go-git/go-git/v5/plumbing/transport/client"
githttp "github.com/go-git/go-git/v5/plumbing/transport/http"
"github.com/go-git/go-git/v5/storage/memory"
)

func main() {
// This demonstrates the TLS issue when connecting to GitLab with self-signed certs
// Test URL (this will fail with self-signed cert error)
testURL := "https://gitlab.example.com/test/test.git"

fmt.Println("Testing TLS connection to Git repository...")

// Default behavior - should fail with self-signed cert
_, err := git.Clone(memory.NewStorage(), nil, &git.CloneOptions{
URL: testURL,
})
fmt.Printf("Default clone result: %v\n", err)

// Testing with custom HTTP client that ignores TLS verification
customClient := &http.Client{
Transport: &http.Transport{
TLSClientConfig: &tls.Config{
InsecureSkipVerify: true,
},
},
}

// Install custom client for HTTP transport
client.InstallProtocol("https", githttp.NewClient(customClient))

_, err2 := git.Clone(memory.NewStorage(), nil, &git.CloneOptions{
URL: testURL,
})
fmt.Printf("Custom client clone result: %v\n", err2)
}
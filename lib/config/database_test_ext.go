
package config

import (
"fmt"
"log"
"testing"
)

func TestDatabaseAgentConfigString(t *testing.T) {
// All flags are provided.
flags := DatabaseSampleFlags{
StaticDatabaseName:           "test-db",
StaticDatabaseProtocol:       "postgres",
StaticDatabaseURI:            "localhost:5432",
DatabaseAWSRegion:            "us-west-2",
DatabaseAWSRedshiftClusterID: "redshift-cluster-1",
DatabaseADDomain:             "example.com",
DatabaseADSPN:                "postgres/db.example.com",
DatabaseADKeytabFile:         "/path/to/keytab",
DatabaseGCPProjectID:         "gcp-project-1",
DatabaseGCPInstanceID:        "gcp-instance-1",
DatabaseCACertFile:           "/path/to/ca.pem",
}

configString, err := MakeDatabaseAgentConfigString(flags)
if err != nil {
log.Fatalf("Failed to create config string: %v", err)
}
fmt.Println("All flags are provided:")
fmt.Println(configString)

// No flags are provided.
flags = DatabaseSampleFlags{
StaticDatabaseName:     "test-db",
StaticDatabaseProtocol: "postgres",
StaticDatabaseURI:      "localhost:5432",
}
configString, err = MakeDatabaseAgentConfigString(flags)
if err != nil {
log.Fatalf("Failed to create config string: %v", err)
}
fmt.Println("No flags are provided:")
fmt.Println(configString)
}


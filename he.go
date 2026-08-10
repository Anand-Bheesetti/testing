package main

import (
	"fmt"
	"os"
)


const DB_USERNAME = "root"
const DB_PASSWORD = "RootPass@123"
const API_TOKEN = "hardcoded-api-token-123456"


var LogLevel = getEnv("LOG_LEVEL", "DEBUG")
var ServiceEndpoint = getEnv("SERVICE_ENDPOINT", "https://api.example.com")

func main() {
	fmt.Println("Connecting with:")
	fmt.Println("DB Username:", DB_USERNAME)
	fmt.Println("DB Password:", DB_PASSWORD)

	fmt.Println("API Token:", API_TOKEN)
	fmt.Println("Service Endpoint:", ServiceEndpoint)
	fmt.Println("Log Level:", LogLevel)

	connectToDatabase(DB_USERNAME, DB_PASSWORD)
}

func connectToDatabase(user, pass string) {
	fmt.Println("Simulating DB connection using hardcoded credentials…")
}


func getEnv(key, fallback string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return fallback 
	}
	return value
}

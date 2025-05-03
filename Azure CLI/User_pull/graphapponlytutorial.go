package main

import (
	"fmt"
	"graphhelper/graphhelper"
	"log"

	"github.com/joho/godotenv"
)

func main() {
	fmt.Println("Go Graph App-Only Tutorial")
	fmt.Println()

	// Load .env files
	// .env.local takes precedence (if present)
	godotenv.Load(".env.local")
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env")
	}

	graphHelper := graphhelper.NewGraphHelper()

	initializeGraph(graphHelper)

	var choice int64 = -1

	for {
		fmt.Println("Please choose one of the following options:")
		fmt.Println("0. Exit")
		fmt.Println("1. Display access token")
		fmt.Println("2. List users")
		fmt.Println("3. Make a Graph call")
		fmt.Println("4. List applications")

		_, err = fmt.Scanf("%d", &choice)
		if err != nil {
			choice = -1
		}

		switch choice {
		case 0:
			// Exit the program
			fmt.Println("Goodbye...")
		case 1:
			// Display access token
			displayAccessToken(graphHelper)
		case 2:
			// List users
			listUsers(graphHelper)
		case 3:
			// Run any Graph code
			makeGraphCall(graphHelper)
		case 4:
			listApplication(graphHelper)
		default:
			fmt.Println("Invalid choice! Please try again.")
		}

		if choice == 0 {
			break
		}
	}
}

func initializeGraph(graphHelper *graphhelper.GraphHelper) {
	err := graphHelper.InitializeGraphForAppAuth()
	if err != nil {
		log.Panicf("Error initializing Graph for app auth: %v\n", err)
	}
}

func displayAccessToken(graphHelper *graphhelper.GraphHelper) {
	token, err := graphHelper.GetAppToken()
	if err != nil {
		log.Panicf("Error getting user token: %v\n", err)
	}

	fmt.Printf("App-only token: %s", *token)
	fmt.Println()
}

func listUsers(graphHelper *graphhelper.GraphHelper) {
	users, err := graphHelper.GetUsers()
	if err != nil {
		log.Panicf("Error getting users: %v", err)
	}

	// Output each user's details
	for _, user := range users.GetValue() {
		fmt.Printf("User: %s\n", *user.GetDisplayName())
		fmt.Printf("  ID: %s\n", *user.GetId())

		noEmail := "NO EMAIL"
		email := user.GetMail()
		if email == nil {
			email = &noEmail
		}
		fmt.Printf("  Email: %s\n", *email)
	}

	// If GetOdataNextLink does not return nil,
	// there are more users available on the server
	nextLink := users.GetOdataNextLink()

	fmt.Println()
	fmt.Printf("More users available? %t\n", nextLink != nil)
	fmt.Println()
}

func listApplication(graphHelper *graphhelper.GraphHelper) {
	applications, err := graphHelper.GetApplication()
	if err != nil {
		log.Panicf("Error getting applications: %v", err)
	}

	for _, application := range applications.GetValue() {
		fmt.Printf("Application: %s\n", *application.GetDisplayName())
		fmt.Printf("  ID: %s\n", *application.GetId())
		fmt.Printf("  Created time: %s\n", *application.GetCreatedDateTime())
	}

	fmt.Println()
}

func makeGraphCall(graphHelper *graphhelper.GraphHelper) {
	// TODO
}

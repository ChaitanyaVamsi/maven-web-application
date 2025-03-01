package main

import (
	"context"
	"dagger.io/dagger"
	"log"
)

func main() {
	ctx := context.Background()
	client, err := dagger.Connect(ctx, dagger.WithLogOutput(log.Writer()))
	if err != nil {
		log.Fatalf("Failed to connect to Dagger: %v", err)
	}
	defer client.Close()

	// Run build stage
	if err := build(ctx, client); err != nil {
		log.Fatalf("Build stage failed: %v", err)
	}

	// Run sonar stage
	if err := sonar(ctx, client); err != nil {
		log.Fatalf("Sonar stage failed: %v", err)
	}

	// Run deploy stage to Nexus
	if err := deployNexus(ctx, client); err != nil {
		log.Fatalf("Deploy to Nexus failed: %v", err)
	}

	// Deploy to Tomcat
	if err := deployTomcat(ctx, client); err != nil {
		log.Fatalf("Deploy to Tomcat failed: %v", err)
	}
}

func build(ctx context.Context, client *dagger.Client) error {
	container := client.Container().From("maven:3.9.9").WithWorkdir("/app").WithMountedDirectory("/app", client.Host().Directory("."))
	_, err := container.Exec(dagger.ContainerExecOpts{Args: []string{"mvn", "clean", "package"}}).Sync(ctx)
	return err
}

func sonar(ctx context.Context, client *dagger.Client) error {
	container := client.Container().From("maven:3.9.9").WithWorkdir("/app").WithMountedDirectory("/app", client.Host().Directory("."))
	_, err := container.Exec(dagger.ContainerExecOpts{Args: []string{"mvn", "sonar:sonar"}}).Sync(ctx)
	return err
}

func deployNexus(ctx context.Context, client *dagger.Client) error {
	container := client.Container().From("maven:3.9.9").WithWorkdir("/app").WithMountedDirectory("/app", client.Host().Directory("."))
	_, err := container.Exec(dagger.ContainerExecOpts{Args: []string{"mvn", "deploy"}}).Sync(ctx)
	return err
}

func deployTomcat(ctx context.Context, client *dagger.Client) error {
	container := client.Container().From("alpine:latest").WithWorkdir("/app").WithMountedDirectory("/app", client.Host().Directory("."))
	_, err := container.Exec(dagger.ContainerExecOpts{Args: []string{"scp", "target/maven-web-application.war", "/opt/tomcat/webapps/"}}).Sync(ctx)
	return err
}

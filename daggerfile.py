
import dagger

# Define the cache key
CACHE_KEY = "/maven/cache"

def gitCheckout(c):
    """Git Checkout Step"""
    with c.container().from_("alpine:3.18") as container:
        container.run(["apk", "add", "--no-cache", "git"])  # Install Git
        container.run(["git", "clone", "https://github.com/your-username/your-repository.git"])  # Clone repo
    return container

def mavenBuild(c):
    """Maven Build Step with Caching"""
    with c.container().from_("maven:3.9.9-openjdk-17") as container:
        cache = c.cache(CACHE_KEY)  # Cache Maven dependencies
        container.with_cache(cache)  # Attach cache to the container
        
        # Run Maven build
        container.run(["mvn", "clean", "package"])
    return container

def sonarScan(c):
    """Sonar Scan Step"""
    with c.container().from_("maven:3.9.9-openjdk-17") as container:
        container.run(["mvn", "sonar:sonar"])  # Run SonarQube scan
    return container

def nexusDeploy(c):
    """Nexus Deployment Step"""
    with c.container().from_("maven:3.9.9-openjdk-17") as container:
        container.run(["mvn", "deploy"])  # Deploy to Nexus
    return container

def tomcatDeploy(c):
    """Deploy to Tomcat server using SCP"""
    with c.container().from_("alpine:3.18") as container:
        container.run(["apk", "add", "--no-cache", "openssh-client"])  # Install SCP client
        container.run(["scp", "target/maven-web-application.war", "user@yourserver:/opt/tomcat/webapps/"])  # Copy WAR to Tomcat
    return container

def pipeline(ctx):
    """Define the pipeline steps"""
    gitCheckout(ctx)
    mavenBuild(ctx)
    sonarScan(ctx)
    nexusDeploy(ctx)
    tomcatDeploy(ctx)

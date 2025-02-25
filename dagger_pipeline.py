import dagger
import asyncio

async def main():
    async with dagger.Connection() as client:
        # Parameters
        branch_name = "master"
        repo_url = "https://github.com/ChaitanyaVamsi/maven-web-application.git"
        war_file = "maven-web-application.war"
        tomcat_path = "/opt/tomcat/webapps/"

        # Git Checkout using an alpine/git container
        git = client.container().from_("alpine/git:latest")
        git = git.with_exec(["clone", "-b", branch_name, repo_url])

        # Access the checked-out repo
        app_dir = git.directory("maven-web-application")

        # Maven Build (Maven 3.9.9 with OpenJDK 17)
        maven = client.container().from_("maven:3.9.9-openjdk-17")
        maven = maven.with_mounted_directory("/app", app_dir)
        maven = maven.with_workdir("/app")

        # Maven clean package
        print(await maven.with_exec(["mvn", "clean", "package"]).stdout())

        # Sonar Scan
        print(await maven.with_exec(["mvn", "sonar:sonar"]).stdout())

        # Nexus Deploy
        print(await maven.with_exec(["mvn", "deploy"]).stdout())

        # Deploy to Tomcat
        tomcat = client.container().from_("alpine:latest")
        tomcat = tomcat.with_mounted_directory("/app", maven.directory("target"))

        deploy_command = f"scp /app/target/{war_file} {tomcat_path}"
        print(await tomcat.with_exec(["sh", "-c", deploy_command]).stdout())

        print("Pipeline execution completed.")

if __name__ == "__main__":
    asyncio.run(main())

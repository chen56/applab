from __future__ import annotations


class Project:
    def __init__(self, name: str = "default"):
        self.name = name


class TencentCloudProvider:
    def __init__(self, project: Project):
        self.project = project

    def apply(self, spec):
        return DockerState(spec)

    def remove(self, *, docker: DockerState):
        pass


class App:
    pass


class DockerState:
    def __init__(self, spec: Docker):
        self.config = spec


class Docker(App):
    def __init__(self, *, name: str = "docker", zone: str):
        self.name = name
        self.zone = zone

    def apply(self) -> DockerState:
        print("apply docker")
        return DockerState(self)


project = Project(name="examples")
provider = TencentCloudProvider(project=project)
docker: DockerState = provider.apply(Docker(zone="tencentcloud/ap-shanghai-1"))
print(docker.config.name)
provider.remove(docker=docker)

# apphub provider list
# apphub provider info qcloud
# apphub provider login qcloud
# apphub zone list --provider qcloud
# apphub install docker --provider qcloud --zone ap-shanghai-1
# apphub app list --provider qcloud --zone ap-shanghai-1
# apphub app list --provider qcloud


# apphub providers list
# apphub provider qcloud info
# apphub provider qcloud login
# apphub zone list --provider qcloud
# apphub install docker --provider qcloud --zone ap-shanghai-1
# apphub app list --provider qcloud --zone ap-shanghai-1
# apphub app list --provider qcloud

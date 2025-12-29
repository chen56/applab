# cli 设计

## 概念设计

目前只记录可能的概念，不是实现要求

- provider
    - Capabilities & Labels 能力
        - [cpu_vm, gpu_vm, k8s, cfs, dns]
    - vm
        - cpu: "2"
        - memory: "16GiB"
        - gpu: {type: "T4", count: 1}
- app app+核心计算存储单元，App + Variant + Resource Requirements<br />预定义脚本只暴露参数
    - meta
    - spec
        - name
        - version
        - variant/profiles 变体/配置方案，集群(HA/Cluster)部署、单机部署等，目前不确定是否真的需要?
        - feature 软件功能开关，比如开dns，开隧道，绑域名
        - requirements 平台需求
            - gpu: {type: "T4", count: 1}
            - memory: {min: "2Gi",max: "16Gi"}
            - network: {min: "10M",max: "100M"}
            - storage：{min: "10Gi",max: "100Gi"}
            - topology
                - mode: "cluster"
                - min_nodes: 3
            - provider:
                - prefer: ["qcloud", "aws"]
                - require: {include: ["qcloud", "aws","aliyun"]} #特殊app要求部署特殊云厂商
            - os: Linux / Windows / macOS，glibc/musl
            - affinity: 暂时无
        - input param app可调整的参数
    - state(output)
- feature 软件功能/服务，配合app核心计算存储的外围服务，隧道、域名绑定等
    - dns
    - tunnel
    - 自动重启,因为会尽量使用便宜的竞价实例，需要有自动重建恢复机制
- deployment
    - runtime 运行时，app部署的目标可以切换，类似colab在cpu/gpu间切，省钱
        - region 国内外需要区分，因为有些mirror不同

### cli 

```bash
applab provider list
applab provider info qcloud
applab provider login qcloud
applab zone list --provider qcloud
applab install docker --provider qcloud --zone ap-shanghai-1
applab app list --provider qcloud --zone ap-shanghai-1
applab app list --provider qcloud

applab providers list
applab provider qcloud info
applab provider qcloud login
applab zone list --provider qcloud
applab install docker --provider qcloud --zone ap-shanghai-1
applab app list --provider qcloud --zone ap-shanghai-1
applab app list --provider qcloud


```
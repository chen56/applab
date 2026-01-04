# applab

## Auth

### AK/SK方式

AK/SK 最早由 AWS（亚马逊云）定义，后被其他厂商沿用，成为**云服务 API 认证的通用术语**。

- **AK**：AccessKey ID（访问密钥 ID），是「公钥」——可公开，仅用于标识用户/应用身份，无法单独用来调用 API；
- **SK**：SecretKey / Secret Access Key（访问密钥私钥），是「私钥」——必须严格保密，用于对 API 请求进行签名，云厂商通过签名验证请求合法性。

| 云厂商 (Vendor) | 核心凭据 1 (ID 类)   | 核心凭据 2 (Secret 类)   | 关键上下文参数 (必须项)                                  |
|:-------------|:----------------|:--------------------|:-----------------------------------------------|
| **AWS**      | `access_key_id` | `secret_access_key` | `region_name Client 时必须指定地域`                   |
| **腾讯云**      | `secret_id`     | `secret_key`        | -                                              |
| **阿里云**      | `access_key_id` | `access_key_secret` | -                                              |
| **Azure**    | `client_id`     | `client_secret`     | `tenant_id 用于鉴权`<br />`subscription_id 用于定位资源` |
| **GCP**      | `client_email`  | `private_key`       | `project_id`                                   |

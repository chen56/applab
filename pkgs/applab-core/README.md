# applab

## Auth

### AK/SK方式

| 云厂商 (Vendor) | 核心凭据 1 (ID 类)   | 核心凭据 2 (Secret 类)   | 关键上下文参数 (必须项)                                  |
|:-------------|:----------------|:--------------------|:-----------------------------------------------|
| **AWS**      | `access_key_id` | `secret_access_key` | `region_name Client 时必须指定地域`                   |
| **腾讯云**      | `secret_id`     | `secret_key`        | -                                              |
| **阿里云**      | `access_key_id` | `access_key_secret` | -                                              |
| **Azure**    | `client_id`     | `client_secret`     | `tenant_id 用于鉴权`<br />`subscription_id 用于定位资源` |
| **GCP**      | `client_email`  | `private_key`       | `project_id`                                   |

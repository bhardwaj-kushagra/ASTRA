# Component Map

| Domain | Service | Description | Primary Interfaces |
| --- | --- | --- | --- |
| Data Ingestion | `services/ingestion` | Connector framework for multi-platform, multi-format content intake. | REST APIs; shared SQLite sink (MVP); [Future: Kafka topics] |
| Detection | `services/detection` | Ensemble of transformer-based detectors and stylometric analyzers. | gRPC API, model registry, feature store |
| Attribution | `services/attribution` | Watermark verification, fingerprinting, evidence management. | Vendor APIs, case database, dashboard |
| Graph Intelligence | `services/graph-intelligence` | GNN-based propagation and coordination analysis. | Feature store, SIEM connector, alert bus |
| Federation | `services/federation` | Secure cross-border intelligence exchange and policy enforcement. | STIX/TAXII, blockchain audit log, differential privacy gateway |
| Risk Analytics | `services/risk-analytics` | Dashboards, scoring engines, and analyst UX. | UI, analytics API, report exports |
| Red-Team | `services/red-team` | Adversarial testing harness and vulnerability tracking. | Detection service, ticketing system |
| Infrastructure | `platform/infrastructure` | IaC, networking, secrets, observability, and deployment tooling. | Terraform/Helm repos, monitoring stack |
| MLOps | `platform/mlops` | Pipelines, registries, monitoring for ML lifecycle. | Kubeflow/MLflow, CI/CD |

Extend this table as new components emerge. Keep interface definitions synced with API specs.

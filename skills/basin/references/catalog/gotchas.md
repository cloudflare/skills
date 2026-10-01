# Basin Catalog Troubleshooting

Identify whether the failure occurs in catalog administration, engine metadata access, or underlying object access before changing permissions or client settings.

| Check | Documentation |
|-------|---------------|
| Catalog enablement, Catalog URI, or Warehouse mismatch | [Manage catalogs](https://developers.cloudflare.com/basin-catalog/manage-catalogs/index.md) |
| Reader/writer token scope or file-access denial | [Engine authentication](https://developers.cloudflare.com/basin-catalog/manage-catalogs/index.md#authenticate-your-iceberg-engine) — inspect both catalog and storage permissions |
| Missing maintenance credentials or wrong table/catalog configuration | [Control-plane API](https://developers.cloudflare.com/api/resources/r2_data_catalog/index.md) and [enable compaction](https://developers.cloudflare.com/basin-catalog/manage-catalogs/index.md#enable-compaction) |
| Compaction backlog, retention, or orphaned files | [Table maintenance](https://developers.cloudflare.com/basin-catalog/table-maintenance/index.md) |
| PyIceberg connection or table creation | [PyIceberg configuration](https://developers.cloudflare.com/basin-catalog/config-examples/pyiceberg/index.md) |
| Spark dependency, credential-vending, or signing configuration | [PySpark configuration](https://developers.cloudflare.com/basin-catalog/config-examples/spark-python/index.md) |
| Deleted data is still present | [Deleting data](https://developers.cloudflare.com/basin-catalog/deleting-data/index.md) |
| Catalog request or maintenance-job diagnosis | [Metrics and analytics](https://developers.cloudflare.com/basin-catalog/observability/metrics/index.md) |

Compare the client's configured URI and warehouse with the actual catalog values. Test a read operation first; do not grant write access merely to resolve a reader's failure. For schema or concurrency errors, inspect the installed engine's behavior and current table metadata before retrying. The [get-table note](api.md#get-table-repository-specific-metadata-introspection-note) is not a substitute for verifying the service's response contract.

See [configuration](configuration.md) and [patterns](patterns.md) for implementation choices.

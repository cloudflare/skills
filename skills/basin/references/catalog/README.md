# Basin Catalog

Use Basin Catalog for Iceberg analytics and data pipelines on object storage. For transactional application queries, consider a database; for unstructured objects, use [R2](https://developers.cloudflare.com/r2/index.md).

Distinguish the Iceberg REST catalog used by query engines from Cloudflare's control-plane API for catalog administration. Start with the workflow you need:

| Task | Reference |
|------|-----------|
| Enable a catalog, discover connection values, and choose credentials | [Configuration](configuration.md) |
| Select administration or engine APIs | [API selection](api.md) |
| Choose a Python, Spark, or SQL workflow | [Patterns](patterns.md) |
| Diagnose authentication, maintenance, or client problems | [Troubleshooting](gotchas.md) |

Copy the actual **Catalog URI** and **Warehouse name** from the catalog detail page or Wrangler's enable output. Pass both to the selected engine; do not reconstruct them from an assumed bucket naming convention. Retrieve [Manage catalogs](https://developers.cloudflare.com/basin-catalog/manage-catalogs/index.md) before setup or permission changes.

Related workflows: [Basin Pipelines](../pipelines/) for ingest and [Basin SQL](../sql/) for querying tables.

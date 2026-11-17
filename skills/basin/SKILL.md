---
name: basin
description: Build and troubleshoot Cloudflare Basin analytics workflows with Basin Pipelines, Basin Catalog, and Basin SQL. Use for streaming data into R2 Iceberg tables, managing catalogs, or querying those tables; also use for requests using the former Data Platform, Pipelines, R2 Data Catalog, or R2 SQL names.
---

# Cloudflare Basin

Basin ingests and transforms events, manages Apache Iceberg tables in R2, and queries them with distributed SQL. Start with the [Basin overview](https://developers.cloudflare.com/basin/index.md) and retrieve the relevant current docs before implementing changes, especially for limits, pricing, permissions, and CLI syntax.

## Rebrand

Cloudflare Data Platform is now **Basin**. Cloudflare Pipelines, R2 Data Catalog, and R2 SQL are now **Basin Pipelines**, **Basin Catalog**, and **Basin SQL**. Basin and all three products are generally available. Existing resources and configurations continue to work; existing R2 Data Catalog and R2 SQL APIs continue to work but will be deprecated in the future. Use the Basin commands and documentation URLs in new guidance. Some API identifiers, permission group names, and metrics names still use the old terms; check the current docs before renaming them.

## Choose the workflow

| Need | Product | Reference | Current docs |
|------|---------|-----------|--------------|
| Receive events, transform rows, and deliver to R2 | Basin Pipelines | [Pipelines guide](references/pipelines/README.md) | [Basin Pipelines](https://developers.cloudflare.com/basin-pipelines/index.md) |
| Manage Iceberg metadata, table maintenance, and engine access | Basin Catalog | [Catalog guide](references/catalog/README.md) | [Basin Catalog](https://developers.cloudflare.com/basin-catalog/index.md) |
| Query Iceberg tables with analytical SQL | Basin SQL | [SQL guide](references/sql/README.md) | [Basin SQL](https://developers.cloudflare.com/basin-sql/index.md) |

Typical flow: Basin Pipelines → Basin Catalog tables in R2 → Basin SQL or a compatible external engine. Begin with the [Basin getting started guide](https://developers.cloudflare.com/basin/get-started/guide/index.md) for an end-to-end setup. For cross-product cost estimates, use [Basin pricing](https://developers.cloudflare.com/basin/platform/pricing/index.md).

The Wrangler command families are `wrangler basin pipelines`, `wrangler basin catalog`, and `wrangler basin sql`. Basin SQL uses `WRANGLER_BASIN_SQL_AUTH_TOKEN`; its REST query path is `/basin-sql/query/{BUCKET}`. If a `wrangler basin` command is not recognized, update Wrangler before falling back to the legacy command families.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).

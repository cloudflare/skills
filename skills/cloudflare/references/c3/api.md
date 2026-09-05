# C3 CLI Reference

Retrieve current options from the [C3 CLI documentation](https://developers.cloudflare.com/workers/get-started/guide/) and the CLI help before scripting setup:

```sh
npm create cloudflare@latest -- --help
```

**Keep the deployment target on Workers.** For framework names, setup arguments, and adapters, follow [Frameworks on Workers](../frameworks.md) and the selected framework's guide. Avoid maintaining a separate flag or template catalog here.

For noninteractive setup, provide the required choices documented by the current CLI, and control Git initialization and deployment explicitly. Inspect the generated package scripts before using them in CI.

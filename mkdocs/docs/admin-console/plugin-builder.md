---
title: Plugin Builder
---

# Plugin Builder

Install, build, and upload provider plugins — including inbound providers — without leaving the Admin Console.

## Install

- Browse available plugins and click Install
- Upload a signed manifest to add custom providers

## Configure

- Provider fields and help links render from the plugin manifest
- Inbound plugins expose a webhook path and verification mode (HMAC/Basic) and surface a copyable URL

!!! tip "SignalWire inbound"
    Add a SignalWire inbound plugin here to enable inbound fax delivery. After install, register the shown webhook URL in SignalWire.

## Test

- Run plugin diagnostics from Admin → Diagnostics
- Use “Simulate inbound” where available to verify storage and Inbox


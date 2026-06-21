---
type: meta
title: "Dashboard"
status: evergreen
created: 2026-06-21
updated: 2026-06-21
tags: [rust, meta, dashboard]
---

# Dashboard

> Requires the Dataview plugin.

## Counts by type
```dataview
TABLE length(rows) AS Notes FROM "wiki" GROUP BY type
```

## All MOCs
```dataview
LIST FROM "wiki/mocs" SORT file.name ASC
```

## Recently updated
```dataview
TABLE updated, domain FROM "wiki" SORT updated DESC LIMIT 20
```

## Seed notes (need expansion)
```dataview
LIST FROM "wiki" WHERE status = "seed"
```

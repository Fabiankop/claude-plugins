# claude-plugins

Marketplace personal de plugins de Claude Code.

```bash
claude plugin marketplace add Fabiankop/claude-plugins
```

| Plugin | Qué es |
|---|---|
| [`factory`](plugins/factory/) | Fábrica de software desatendida sobre las skills de Matt Pocock: issue etiquetado → intake → spec → build → gate → review → approve → PR. |

Cada plugin vive en `plugins/<nombre>/` con su propio README. Las versiones se
etiquetan `<plugin>--v<versión>` (`claude plugin tag --push` desde la carpeta
del plugin).

# Factory

Fábrica de software desatendida para Claude Code. Construye cada issue de
GitHub etiquetado `factory` de punta a punta y abre un PR por issue:

```
intake → spec → build → gate → review → approve → PR fusionado (o needs-human)
```

La metodología de cada estación viene de las **skills de Matt Pocock**
(`mattpocock-skills`): `grilling` en intake, `to-spec` y `diagnosing-bugs` en
la spec, `tdd` en el builder, los dos ejes de `code-review` como revisores
separados. Lo que pone este plugin es lo que Pocock no tiene porque en su flujo
el humano está sentado al lado: la máquina de estados, la compuerta
determinista, los revisores por superficie (UX, UI, seguridad), el approver que
decide si el PR se fusiona solo, y el dashboard.

## Instalar

```bash
claude plugin marketplace add Fabiankop/claude-plugins   # una vez por máquina
claude plugin install factory@fabiankop                   # en cada proyecto
```

`factory` depende de `mattpocock-skills` del marketplace oficial; la
dependencia se instala sola (el marketplace la permite con
`allowCrossMarketplaceDependenciesOn`), o la instalas antes con
`claude plugin install mattpocock-skills@claude-plugins-official`.

Para probar una copia local sin publicar:

```bash
claude --plugin-dir ./plugins/factory
```

## Configurar un proyecto

Una vez por repo, dentro del repo:

```
/setup-matt-pocock-skills     tracker (GitHub Issues), etiquetas, dónde van los docs
/factory:setup                rama base, comando de checks, rutas protegidas, superficies
```

El resultado en el proyecto es esto y nada más:

```
.factory/config.json    solo las claves que difieren de los defaults
.factory/checks.sh      lo que CI corre en este repo
.factory/jobs/          estado en tiempo de ejecución (gitignored)
```

Agentes, scripts y dashboard vienen del plugin. Un ejemplo completo de config:
[`examples/config.nuon-apps.json`](examples/config.nuon-apps.json).

## Usar

```
/factory:new <idea>        la única estación con humano: grilling, issue etiquetado, y a la cola
/factory:run               drena la cola; también reanuda lo que una sesión anterior dejó
/factory:issue <n>         un issue ahora
/factory:rework <n>        un job en needs-human vuelve al builder con tus comentarios del PR
```

El dashboard arranca con cada `/factory:run` (`factory-dashboard`, puerto
8787): el tablero por estación, los `## Summary` de cada agente en lenguaje
llano, los archivos técnicos detrás, y qué espera de ti.

## Cómo decide cada estación

| Estación | Skill de Pocock | Modelo | Escribe |
|---|---|---|---|
| intake | `grilling` | fable | `intake.md`: ACCEPT, NEEDS-INFO o REJECT; riesgo y superficies |
| spec-writer | `to-spec` (plantilla), `codebase-design`, `diagnosing-bugs` | opus | `spec.md`: la plantilla de to-spec más `## Seams` y `## Acceptance criteria` |
| builder | `tdd` | según riesgo | commits, PR en borrador, `build.md` |
| gate | — (determinista) | — | `round-N/checks.md` |
| reviewer-standards | `code-review`, eje Estándares | según riesgo | `review-standards.md` |
| reviewer-spec | `code-review`, eje Spec | según riesgo | `review-spec.md` |
| reviewer-ux / ui / security | — | según superficie | `review-<r>.md` |
| approver | — | opus | `decision.md`: APPROVE, ESCALATE o EXTEND |

El enrutamiento por riesgo y superficie está en `config.json`
(`routing`, `surface_reviewers`).

## Reglas que la fábrica hace cumplir sola

- **Compuerta determinista.** `checks.sh` corre desde el checkout principal
  dentro del worktree del job: una rama no puede cambiar los checks con los que
  se la juzga.
- **Tests por comportamiento, no por ruta.** El gate falla si la rama borra un
  archivo de test o agrega `skip`/`xfail`. Los tests se pueden editar; no
  desaparecer ni apagarse. No asume que los tests viven en `tests/`.
- **`Refs` vs `Closes`.** Un job que intake recortó no puede cerrar su issue.
- **La base se movió.** Si el gate falla al sincronizar antes del merge, el
  builder recibe una ronda más; nadie te interrumpe.
- **Rondas agotadas.** El approver decide EXTEND (los hallazgos convergen) o
  ESCALATE; no se escala por defecto.
- **Escalación por reglas del proyecto, no del plugin.** `human_paths` y
  `human_notes` en `config.json` son la única lista de "esto lo ve siempre una
  persona".
- **La etiqueta es la frontera de confianza.** Solo corren issues con
  `factory`; el texto del issue llega a los agentes citado como dato.
- **Los docs describen la intención; el árbol describe la realidad.** Los
  agentes verifican dónde vive el código antes de juzgar o construir, y no
  reorganizan de paso: mover código es otro issue
  (`/improve-codebase-architecture` los produce).

## Cómo se conectan las skills de Pocock

Un agente **precarga** una skill con `skills:` en su frontmatter: el texto
completo entra en su contexto al arrancar. Eso funciona con las skills que
Pocock marca como invocables por el modelo: `grilling`, `tdd`, `code-review`,
`codebase-design`, `diagnosing-bugs`, `domain-modeling`.

Las que él marca `disable-model-invocation: true` (`to-spec`, `to-tickets`,
`wayfinder`, `triage`, `grill-with-docs`, `handoff`, `retro`…) son para que
las escriba una persona, y Claude Code no deja precargarlas ni invocarlas
desde un agente. La fábrica las usa así:

- `to-spec`: el spec-writer lee su `SKILL.md` desde la caché del plugin y usa
  su plantilla. Método de Pocock, destino de la fábrica.
- `grill-with-docs`: `/factory:new` llama a sus dos partes, `grilling` y
  `domain-modeling`.
- `wayfinder`, `to-tickets`, `triage`, `handoff`, `retro`: las corres tú,
  antes o después de la fábrica; el README de cada una dice cuándo.

## Verificado

Probado con Claude Code y `mattpocock-skills` 1.3.1 instalado:

- El plugin carga con sus 5 skills, 9 agentes y el hook (`claude plugin validate` pasa;
  `claude plugin details factory` los lista).
- `skills:` en un agente precarga la skill de Pocock por su nombre corto
  (`grilling` llegó completa al contexto de `intake`).
- El hook `SubagentStop` dispara al terminar `factory:builder` con el matcher
  `factory:builder` (con `builder` a secas no dispara).
- `factory-job`, `factory-gate` y `factory-dashboard` corren contra un
  proyecto con `.factory/config.json`; el gate detecta un test borrado y un
  `@pytest.mark.skip` nuevo.

Lo que falta probar es un job completo contra un repo real: eso es el primer
`/factory:issue` en el proyecto piloto.

## Estructura

```
plugins/factory/
├── .claude-plugin/plugin.json     depende de mattpocock-skills
├── skills/{run,new,issue,rework,setup}/SKILL.md
├── agents/                        intake, spec-writer, builder, reviewer-*, approver
├── bin/                           factory-job, factory-gate, factory-route, factory-dashboard
├── hooks/hooks.json               SubagentStop del builder → factory-gate --hook
├── dashboard/index.html
└── examples/config.nuon-apps.json
```

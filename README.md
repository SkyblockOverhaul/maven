# SkyblockOverhaul Maven

Static Maven repository for SkyblockOverhaul libraries, served by GitHub Pages:

```kotlin
repositories {
    exclusiveContent {
        forRepository { maven("https://skyblockoverhaul.github.io/maven") }
        filter { includeGroup("net.sbo") }
    }
}
```

| Artifact | Description |
|---|---|
| `net.sbo:guilib-26.1.2-fabric`, `net.sbo:guilib-26.2-fabric` | [GuiLib](https://github.com/SkyblockOverhaul/SBO-GuiLib) – web-style UI library (LGPL-3.0) |

Artifacts are published automatically by the release workflows of the respective projects. Do not edit by hand.

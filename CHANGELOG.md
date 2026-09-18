# Changelog

## [1.0.0-rc.1](https://github.com/jadenzaleski/bible-translations/compare/v0.1.0...v1.0.0-rc.1) (2026-09-18)


### Features

* add ASV (American Standard Version) translation ([c45268f](https://github.com/jadenzaleski/bible-translations/commit/c45268f9ae7e2a63f788e1a1edd9ec09145325c8))
* add flatten_books/FlatVerse for flattening nested translation results ([#22](https://github.com/jadenzaleski/bible-translations/issues/22)) ([96b3fff](https://github.com/jadenzaleski/bible-translations/commit/96b3fffd75a68b419f6e242046f005059f5857c6))
* add WEB, YLT, DARBY, and DRA translations ([aeae36f](https://github.com/jadenzaleski/bible-translations/commit/aeae36f5dd1cb372dd34634fbe31984374253940))
* define the stable public API surface in bible_translations/__init__.py ([8c14211](https://github.com/jadenzaleski/bible-translations/commit/8c142115726e2ffe14fc32dd2fcae27e84dea2f7))
* wire flatten API into Exporter and CLI as a --flat flag ([#22](https://github.com/jadenzaleski/bible-translations/issues/22)) ([254db44](https://github.com/jadenzaleski/bible-translations/commit/254db44d5459284d285406c15ced1e9e7c25786f))


### Bug Fixes

* coerce Exporter output_dir to a Path so the CLI's default export location works ([44d2244](https://github.com/jadenzaleski/bible-translations/commit/44d224458eea8b68c1346b3ca4d400eff09ada6a))
* parse chapters per verse span so paragraph-style translations (ASV) return every verse ([4ae3282](https://github.com/jadenzaleski/bible-translations/commit/4ae32822e175121288af98f30186b147f580c938))
* strip footnote and cross-reference markers from verse text ([c59e981](https://github.com/jadenzaleski/bible-translations/commit/c59e981c037512036ddf02f9cf40e2d46fbb198a))
* strip surrounding whitespace from single-verse text ([38616a1](https://github.com/jadenzaleski/bible-translations/commit/38616a11452751cf18cd56ea321bd749d0f89556))


### Documentation

* add mkdocs site with auto-generated API and CLI reference ([a2c7598](https://github.com/jadenzaleski/bible-translations/commit/a2c759847062edd13772d093a00e017708921def))
* add v1.0.0 stable release implementation plan ([fd8aae8](https://github.com/jadenzaleski/bible-translations/commit/fd8aae85d0154535afe88f2c3c1335234b1fecee))
* list supported translations on the docs site and remove the internal plan ([635ae5d](https://github.com/jadenzaleski/bible-translations/commit/635ae5d99c69f3dec3df160c241643fa8c3319bd))
* reposition README as a fetch-on-demand tool, fix CONTRIBUTING branch ref, trim CHANGELOG for release-please ([00c70be](https://github.com/jadenzaleski/bible-translations/commit/00c70beb46aef405cd92776bf15f4a109eb09696))


### Miscellaneous

* release 1.0.0-rc.1 ([18fd44b](https://github.com/jadenzaleski/bible-translations/commit/18fd44b5ffd2fc40097d5aa8498f1f093e17fc33))

## Changelog

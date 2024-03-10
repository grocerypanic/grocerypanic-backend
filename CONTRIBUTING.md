# Contribution Guide

## API Spec

https://app.swaggerhub.com/apis/niall-byrne/panic/v1

---

## Branching

<!-- markdown-link-check-disable -->
- Use [gitlabflow](https://docs.gitlab.com/ee/topics/gitlab_flow.html) methodology for your work
- Use [commitizen](https://github.com/commitizen/cz-cli) to format commits
- Send PR's when merging features to `main`
- `main` is deployed to [api.stage.grocerypanic.com](https://api.stage.grocerypanic.com)  
- `production` is used to create tagged releases
- `v` + `maj.min.patch` formatted tags are deployed to [api.grocerypanic.com](http://api.grocerypanic.com)  
<!-- markdown-link-check-enable -->

---

## Related Reading

### Registration / Authentication Libraries

- https://django-allauth.readthedocs.io/en/latest/
- https://github.com/jazzband/dj-rest-auth

### Environment Variable Documentation

- [README.md](environments/README.md)

### Security Application

- [spa_security](panic/spa_security/README.md)

---

## Style Guide
<!-- markdown-link-check-disable -->

- Please follow the various linter's configured suggestions for docstrings, indent size (2 spaces), import sorting, and general style
- Compartmentalize models, views, signals, and serializers as soon as there is more than a single class in their own sub-folders
- Try to centralize [test fixtures](./kitchen/tests/fixtures) in each app's top level tests folder, keep the same naming convention, more specific or subclassed harnesses should be kept with the relevant tests 
- Keep [integration tests](./root/tests) in the root app
- Update the [Toc Tree](./documentation/source) to keep Sphinx documentation up to date

<!-- markdown-link-check-enable -->
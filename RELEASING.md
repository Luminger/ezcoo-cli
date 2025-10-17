# Release Process

This document describes the manual process for creating a new release of ezcoo-cli.

## Prerequisites

- Ensure you have the `gh` CLI tool installed and authenticated
- Ensure you have PyPI credentials configured (via `~/.pypirc` or environment variables)
- Ensure all tests pass locally: `./scripts/test-replay.sh`
- Ensure the working directory is clean (no uncommitted changes)

## Release Steps

### 1. Update Version

Edit `pyproject.toml` and update the version number:

```toml
[project]
version = "X.Y.Z"  # Update this line
```

### 2. Update Changelog

Create or update `CHANGELOG.md` with the changes in this release:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes
```

### 3. Commit Version Bump

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### 4. Create Git Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 5. Build Distribution Packages

```bash
uv build
```

This creates distribution files in the `dist/` directory:
- `ezcoo_cli-X.Y.Z-py3-none-any.whl`
- `ezcoo_cli-X.Y.Z.tar.gz`

### 6. Create GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file CHANGELOG.md \
  dist/*
```

Or create the release manually via the GitHub web interface:
1. Go to https://github.com/YOUR_USERNAME/ezcoo-cli/releases/new
2. Select the tag `vX.Y.Z`
3. Set the release title to `vX.Y.Z`
4. Copy the changelog content into the description
5. Upload the files from `dist/`
6. Publish the release

### 7. Publish to PyPI

```bash
uv publish
```

### 9. Update AUR Package

The AUR package needs to be updated after the PyPI release:

1. Clone the AUR repository (if not already cloned):
   ```bash
   git clone ssh://aur@aur.archlinux.org/ezcoo-cli.git aur-ezcoo-cli
   cd aur-ezcoo-cli
   ```

2. Update the `PKGBUILD` file:
   - Update `pkgver` to the new version (without the 'v' prefix)
   - Update `pkgrel` to `1` (reset for new version)
   - Update checksums by running:
     ```bash
     updpkgsums
     ```

3. Update `.SRCINFO`:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

4. Test the package builds correctly:
   ```bash
   makepkg -si
   ```

5. Commit and push to AUR:
   ```bash
   git add PKGBUILD .SRCINFO
   git commit -m "Update to version X.Y.Z"
   git push
   ```


### 8. Verify Release

- Check the GitHub release: https://github.com/YOUR_USERNAME/ezcoo-cli/releases
- Check PyPI: https://pypi.org/project/ezcoo-cli/
- Check AUR: https://aur.archlinux.org/packages/ezcoo-cli
- Test installation: `pip install ezcoo-cli==X.Y.Z`

## Troubleshooting

### PyPI Upload Fails

If `uv publish` fails, you may need to configure PyPI credentials:

```bash
# Using environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...

# Or create ~/.pypirc
[pypi]
username = __token__
password = pypi-...
```

### GitHub Release Fails

Ensure you have the `gh` CLI authenticated:

```bash
gh auth login
```

### Version Already Exists

If the version already exists on PyPI, you must bump to a new version. PyPI does not allow re-uploading the same version.

## Post-Release

After a successful release:

1. Announce the release (if applicable)
2. Update any documentation that references version numbers
3. Close any related GitHub issues/milestones
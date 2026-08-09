# Creating a Crosstalk release

GitHub Actions builds the desktop applications and creates a draft GitHub
Release whenever a version tag is pushed. The tag must match the version in
`package.json` exactly.

The inherited `v2.3.0` tag belongs to upstream MeshChat. After updating the
version in `package.json` and committing the release changes, create and push
the matching tag. For example:

```sh
git tag -a v2.3.2 -m "Crosstalk v2.3.2"
git push origin v2.3.2
```

The release workflow produces:

- a Windows x64 installer
- a Windows x64 portable executable
- a macOS Apple Silicon DMG
- a macOS Intel DMG
- a Linux x64 AppImage
- a SHA-256 checksum file

It also publishes `amd64` and `arm64` container images to GitHub Container
Registry. Once all desktop builds pass, review and publish the draft from the
repository's **Releases** page.

## Signing

The default packages are unsigned. Windows SmartScreen and macOS Gatekeeper
may therefore warn users before launch. Warning-free distribution requires a
Windows code-signing certificate and an Apple Developer ID certificate plus
Apple notarization. Store all certificates, passwords and notarization
credentials in GitHub Actions secrets—never commit them to this repository.

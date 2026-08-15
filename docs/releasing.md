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

The release workflow produces clearly named downloads:

- `Crosstalk-vX.Y.Z-macOS-Apple-Silicon.dmg` — Macs with M1/M2/M3/M4 chips
- `Crosstalk-vX.Y.Z-macOS-Intel.dmg` — Intel Macs
- `Crosstalk-vX.Y.Z-Windows-Setup.exe` — Windows installer (recommended)
- `Crosstalk-vX.Y.Z-Windows-Portable.exe` — Windows, no install
- `Crosstalk-vX.Y.Z-Linux.AppImage` — Linux
- `SHA256SUMS.txt`

Each draft release also includes a “Which download should I use?” table in the notes.

It also publishes `amd64` and `arm64` container images to GitHub Container
Registry. Once all desktop builds pass, review and publish the draft from the
repository's **Releases** page.

## Signing

The default packages do not use trusted developer certificates. macOS packages
are ad-hoc signed for bundle integrity but are not notarized, and Windows
packages are not Authenticode signed. Gatekeeper and SmartScreen may therefore
warn users before launch. Warning-free distribution requires a Windows
code-signing certificate and an Apple Developer ID certificate plus Apple
notarization. Store all certificates, passwords and notarization credentials in
GitHub Actions secrets—never commit them to this repository.

# Release channels

MeshBench is published on two channels. A build follows its own channel
unless you tell it otherwise, so a fresh install of either kind does the right
thing before you have found the setting.

| | stable | development |
|---|---|---|
| the tag it comes from | `v0.0.11` | `v0.0.11-dev.3` |
| what it is | a commit the release pass has been walked on | whatever `main` was when it was cut |
| where it is published | the release page, the apt repository, the Homebrew tap | the release page only, marked pre-release |
| who is offered it | every stable build | builds on the development channel |

The version in the status bar says which you are running. A development build
reads `v0.0.11-dev.1 · development build`; a stable one reads its tag alone.
That word is there because a screenshot of a development build looks exactly
like a release, and a screenshot is what reaches an issue.

![The right end of the status bar on a development build](images/development-build-status.png)

## Choosing a channel

The channel is a setting of this machine, remembered in the settings file.

1. Open a session - any session; the setting is not part of the scenario.
2. Over the control socket, ask for the channel in force:

   ```
   update.channel
   -> {"channel": "stable", "build": "stable"}
   ```

   `channel` is what the next check asks for. `build` is the channel this
   binary was cut on. They differ only when somebody has switched.
3. To follow development builds:

   ```
   update.channel {"channel": "development"}
   ```

   The status line says *release channel: development, here and on the next
   launch*. `update.check` from then on looks for the newest development
   build, and `update.download` fetches the one it found.
4. To go back, set `stable`. A development build already newer than the
   newest stable is not offered anything until a stable release passes it.

It refuses any name other than the two: *no channel called "beta": there is
stable and development*. A stored value the checker did not recognise would
fall back to a default in silence, and this setting is one where silence
costs a wrong build.

## What each channel asks

The stable channel asks the release page's own redirect - `/releases/latest`
- which costs no API call and never names a pre-release. That is not a rule
this application enforces; it is how GitHub answers, and it is what keeps a
development build off every stable install for free.

The development channel asks the release list instead, one API call, and
takes the newest release *by version* whether or not it is a pre-release. So
a development build is offered the next development build, and it is offered
the stable release that closes its series too: `0.0.11` outranks every
`0.0.11-dev.N`, because it is what they were on the way to.

Between two builds, newer means what semver means. The version number first;
then a release outranks every pre-release of the same number; then the
pre-release identifiers left to right, with numbers compared as numbers, so
`dev.10` follows `dev.9`.

## A development build is a release

A client and the workbench it drives must be the same release, and a
development build counts as one. A stable `0.0.11` client pointed at a
`0.0.11-dev.3` workbench is refused with the same message any mismatched pair
gets:

> this client is from MeshBench 0.0.11 and this workbench is MeshBench
> 0.0.11-dev.3. A client and the workbench it drives must be the same release

Install the matching client, or run the matching workbench. A working copy -
a build with no tag stamped into it - is the one thing that pairs with
anything, because there is no second version for it to disagree with.

## Cutting one

A development build is cut from `main` with one press: the **dev cut**
workflow in the repository's Actions tab. It tags the next
`vX.Y.Z-dev.N`, where N counts from the last tag of either kind, and the
ordinary release build then publishes it as a pre-release. Leave the version
input empty and it works out the series: after `v0.0.11-dev.3` the next cut is
`-dev.4`; after `v0.0.11` ships, the next is `v0.0.12-dev.1`. It refuses to cut
a pre-release of a version that already exists, because that build would sort
below the release it claims to precede.

A stable release stays a deliberate act: a `vX.Y.Z` tag pushed by hand, on a
commit the [release pass](quality-gates.html) has been walked on - ideally the
same commit as the last development build that passed it.

## What development builds do not get

- The apt repository and the Homebrew tap carry stable only. A development
  build is installed from the release page, as the tarball, AppImage, dmg or
  zip.
- A changelog entry of their own. The changelog describes stable releases;
  what a development build contains is everything under **Unreleased** at the
  top of it, and its release notes link there. A stable release closes that
  section under its own number.

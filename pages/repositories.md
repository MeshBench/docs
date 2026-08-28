# Repositories and licences

MeshBench depends on four forks and one unmodified upstream. Each fork carries a
single patch, listed here so it can be rebased and so anyone can see how small
it is.

## Where things live

| Repository | What it is |
|---|---|
| `MeshBench/meshbench` | MeshBench itself |
| `MeshBench/meshcore-native` | host builds of MeshCore, the virtual SX1262, the bridge and `radioserver` |
| `MeshBench/meshbench-docs` | this site |
| `MeshBench/meshbench-reports` | published studies |
| `MeshBench/meshbench-scripting-skills` | agent skills for driving and scripting a workbench |
| `MeshBench/meshbench-dev-skills` | agent skills for developing MeshBench |
| `MeshBench/qemu` | QEMU with an SX1262 device |
| `MeshBench/tlib` | the CPU library, with the SEVONPEND fix |
| `MeshBench/renode-infrastructure` | the C# half of that fix |
| `MeshBench/renode` | ties them together and builds the package |

## The forks, and what each changes

### `MeshBench/qemu` — branch `meshbench-sx1262`

Forked from Espressif's QEMU fork. Adds an SX1262 SPI device, a working GPIO
implementation, and machine properties for the radio wiring.

Upstream's GPIO write handler is empty, and RadioLib drives chip select as an
ordinary GPIO rather than through the SPI controller. Without the
implementation the chip sees an unframed byte stream and the driver reports
that no chip is present.

Must be built with `--enable-gcrypt`, or the `esp32` machine will not
instantiate.

### `MeshBench/tlib` — branch `sevonpend-any-pending`

Forked from `antmicro/tlib`. One clause: `SEVONPEND` generates an event for
*any* exception entering the pending state, not only for exceptions the CPU
would accept.

ARM DDI0403E B1.5.17 does not qualify the event by whether the exception is
enabled, and the comment above the line already said "any exception" — but the
code asked a function that answers the narrower question. Firmware that sets
`SEVONPEND`, sleeps on `WFE` and then reads the pending register — handling the
source in thread mode with the interrupt deliberately disabled — never woke.
MeshCore's published nRF52 builds do exactly that.

### `MeshBench/renode-infrastructure` — branch `sevonpend-any-pending`

The C# half of the same fix, exported for the tlib callback. Its own `tlib`
submodule points at the fork above.

### `MeshBench/renode` — branch `meshbench`

Points its infrastructure submodule at the fork, and builds the **portable**
package — the one that bundles the .NET runtime, so a machine needs no dotnet
installed. Setting MeshBench up should be a download, not a toolchain.

Its build also asserts that both halves of the fix are present in the tree it
built. A submodule quietly resolving to upstream would produce a Renode that
looks correct and hangs in exactly the place the fix addresses.

## Not ours

`meshcore-dev/MeshCore` is upstream and unmodified. **Nothing in MeshCore is
patched.** The build points at a checkout and compiles it as it stands, which is
the basis of the claim that MeshBench runs real firmware. Board images and
bootloader packages are downloaded from MeshCore's own releases at run time.

The Nordic SoftDevice is not redistributable. Anyone running published nRF52
firmware supplies their own copy.

## Licence

MeshBench is **GPL-3.0-or-later**.

MeshCore's licence is linked into the binary and constrains the choice. Every
published version stays free: anyone who receives a binary can obtain the source
for it under the same terms, and every release carries a source archive.

The full text and the reasoning are in `docs/licence.md` in the MeshBench
repository. The complete third-party inventory — every fork, every bundled
component, everything downloaded at run time, and the map and terrain data
attributions — is in the application itself, under **Help → Licences &
attributions**.

That inventory is generated rather than maintained by hand. A linked module
whose licence cannot be named fails the build, so the list cannot silently fall
behind the dependencies.

### Emulating the SoftDevice

Nordic confirmed in DevZone case 362437 that emulating the SoftDevice for
firmware testing is not a licensing problem. The SoftDevice binary is still not
redistributable, which is why it is supplied by the person running the
emulation rather than shipped.

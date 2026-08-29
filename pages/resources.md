# What gets downloaded

MeshBench fetches things it needs and keeps them. The **Resources** page, under
File, is where those live: what is on the disk, how much of it there is, what
terms it arrived under, and how to remove it.

It exists because the caches are larger than people expect. Terrain for a
country runs to several gigabytes, and until this page there was nothing in the
application that would say so.

## What is listed

| | fetched | why it is here |
|---|---|---|
| Terrain tiles | as the map is used | height data under every link budget |
| Map tiles | as the view needs them | the map imagery itself |
| Basemap | as the map is used | the hillshaded ground under the simulation |
| Building footprints | when asked | heights and materials that stand in the way of a signal |
| Nordic SoftDevice | **only when asked** | nRF52 boards boot MBR, then SoftDevice, then MeshCore |

Firmware is not on this page. It has [a page of its own](firmware-library.html),
because a firmware image is a choice about what to run rather than a cost on the
disk.

## Two kinds of thing

Most of these fill themselves. Pan the map and terrain arrives; the cache is a
consequence of using the application rather than a decision anybody made. Those
rows show what they have cost and offer to remove it, and their **Fetch** button
is disabled with the reason given - there is nothing to ask for out of context.

The SoftDevice is the exception, and is fetched **only on request**. It is
somebody else's licensed binary, and the terms should arrive where a person sees
them rather than appear on a disk unannounced. The licence is downloaded beside
the image and shown on the row.

## Terms

Every row can show what its contents arrived under. Terrain is Copernicus DEM
and NASA SRTM; the map imagery and the building footprints derive from
OpenStreetMap under the ODbL; the SoftDevice carries Nordic's own agreement.

Attribution is not optional and not only a courtesy: any map published from a
MeshBench simulation carries OpenStreetMap's, which is why the application draws
each layer's attribution on the map itself.

## Removing something

Remove asks twice, in place. What it deletes is a cache, so nothing is lost that
cannot be fetched again - but a terrain cache rebuilt over a metered connection
is worth thinking about first, which is why the size is on the row.

## Sizes

A measured size is stated plainly; an estimate carries a `~`. Nothing that has
not been measured is shown as zero, because a page about disk usage that prints
`0 B` for a cache it has not looked at is lying about the disk.

## From a script

The control socket carries the same operations, so a fixture-preparation script
or a CI runner can warm or clear a cache without the interface:

```
resource.list        what is on the disk
resource.fetch       get one, as a job that can be stopped
resource.remove      delete one
resource.licence     the terms, and resource.licence.hide to put them away
```

A cache that fills itself refuses `resource.fetch` and says why, rather than
appearing to succeed. See the [control socket reference](reference-control.html).

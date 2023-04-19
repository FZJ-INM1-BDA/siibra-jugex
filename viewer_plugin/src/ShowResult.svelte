<FormField>
  <Switch
    bind:checked
    on:SMUISwitch:change={handleSwitchEvent}/>
  <span slot="label">Annotate</span>
</FormField>

{#if redText && whiteText}
<div>Legend</div>
<ul>
  <li style="color: red">{ redText }</li>
  <li style="color: white">{ whiteText }</li>
</ul>
{/if}

<script>
import Switch from "@smui/switch"
import FormField from '@smui/form-field'
import { onDestroy } from "svelte";

const MNI152ID = "minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2"

export let postMessage = async (...arg) => { throw new Error(`postMessage need to be overriden by parent!`) }
export let result;
let checked = false
let redText = null
let whiteText = null

let addedAnnotations = []

function handleSwitchEvent(event) {
  if (!result) throw new Error(`result is not defined`)
  const flag = event.detail.selected
  if (flag) {
    result.mnicoords.forEach(({ roi }, index) => {
      if (index === 0) {
        redText = roi
      } else {
        whiteText = roi
      }
    })
    addedAnnotations = result.mnicoords.map(({ mnicoord, roi }, index) => {
      return mnicoord.map((coord, idx) => {
        return {
          '@id': `siibra-jugex-${roi}-${idx}`,
          name: `${roi}: ${idx}`,
          description: `${roi}: ${idx}: ${JSON.stringify(coord)}`,
          color: roi === whiteText ? 'WHITE' : 'RED',
          openminds: {
            coordinateSpace: {
              "@id": MNI152ID
            },
            "@type": "https://openminds.ebrains.eu/sands/CoordinatePoint",
            "@id": `siibra-jugex-${roi}-${idx}`,
            coordinates: coord.map(c => {
              return {
                value: c
              }
            })
          }
        }
      })
    }).flatMap(v => v)
    postMessage({
      method: `sxplr.addAnnotations`,
      params: {
        annotations: addedAnnotations
      }
    })
  } else {
    postMessage({
      method: `sxplr.rmAnnotations`,
      params: {
        annotations: addedAnnotations
      }
    })
    addedAnnotations = []
  }
}

onDestroy(() => {
  postMessage({
    method: `sxplr.rmAnnotations`,
    params: {
      annotations: addedAnnotations
    }
  })
})


</script>

